#!/usr/bin/env python
# coding: utf-8
#
# Usage: 
# Author: wxm71(weixing.mei@aispeech.com)

import logging
import threading
import numpy as np
import mxnet as mx
import multiprocessing

from multiprocessing import Queue 

from .utils import batchify
from .generator import NceLabGenerator

class NceCorpusIter(mx.io.DataIter):
    def __init__(self, source, batch_size, bptt, numlab, negative, num_parall=10):
        super(NceCorpusIter, self).__init__()
        self.logger = logging.getLogger('NceCorpusIter')

        # [num_of_batch, batch_size]
        self.source_ = batchify(np.array(source), batch_size)

        self.batch_size = batch_size 
        self.bptt = bptt
        self.numlab = numlab
        self.num_parall = num_parall
        self.negative = negative

        self.queue = Queue(20)
        self.ppoll = []

        label_shape = (bptt, batch_size, numlab)
        self.provide_label = [
                mx.io.DataDesc(name='label', shape=label_shape, dtype='int32'),
                mx.io.DataDesc(name='label_weight', shape=label_shape, dtype='float32')]
        self.provide_data = [mx.io.DataDesc(name='data', shape=(bptt, batch_size), dtype='int32')]

        self._start_generator()


    def _start_generator(self):
        if self.queue.qsize()>0:
            self.logger.warning('queue is not empty, just skip')
            return 
        else:
            flag = False
            for t in self.ppoll:
                flag = t.is_alive()
                if flag: 
                    break
            if flag:
                self.logger.warning('exist alive thread, skip corpus iter start')

        def target_func(data, idxbeg, idxend, batch_size, bptt, numlab, negative, queue):
            generator = NceLabGenerator (data, idxbeg, idxend, batch_size, bptt, numlab, negative, queue)
            generator.run()

        self.ppoll = []
        nbatch = int(self.source_.shape[0]/self.bptt)

        num_parall = self.num_parall
        if nbatch<num_parall:
            num_parall = nbatch

        nstep = int(nbatch/num_parall)*self.bptt
        idxbeg = 0
        for i in range(0, num_parall-1): 
            pid = multiprocessing.Process(target=target_func, args=(self.source_, idxbeg, idxbeg+nstep,
                    self.batch_size, self.bptt, self.numlab, self.negative, self.queue) )
            pid.start()
            self.ppoll.append(pid)
            idxbeg += nstep

        idxend = len(self.source_)-1
        pid = multiprocessing.Process(target=target_func, args=(self.source_, idxbeg, idxend,
            self.batch_size, self.bptt, self.numlab, self.negative, self.queue) )
        pid.start()
        self.ppoll.append(pid)

        # start job end thread
        def jobend_proc():
            for pid in self.ppoll:
                pid.join()
            self.logger.info('all data generator finished')
            self.queue.put(None)
        self.jobend_pid = threading.Thread(target=jobend_proc)
        self.jobend_pid.start()


    def _stop_generator(self):
        self.logger.info('wait for backend generator exit')
        self.jobend_pid.join()
        self.logger.info('data generation done')


    def getdata(self):
        return self._next_data


    def getlabel(self):
        return self._next_label


    def iter_next(self):
        batchdata = self.queue.get()
        if batchdata is None:
            return False
        else:
            self._next_data = [ batchdata[0] ]
            self._next_label = [ batchdata[1], batchdata[2] ] 
        return True


    def next(self):
        if self.iter_next():
            return mx.io.DataBatch(data=self.getdata(), provide_data=self.provide_data,
                    label=self.getlabel(), provide_label=self.provide_label)
        else:
            self._stop_generator()
            raise StopIteration


    def reset(self):
        self._start_generator()
