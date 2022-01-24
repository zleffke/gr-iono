#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022, Zach Leffke


import numpy
from gnuradio import gr
from gnuradio import uhd
import pmt
import time


class usrp_ntp_pps_sync(gr.sync_block):
    """
    docstring for block usrp_ntp_pps_sync
    """
    def __init__(self, parent, usrp_id, verbose):
        gr.sync_block.__init__(self,
            name="usrp_ntp_pps_sync",
            in_sig=None,
            out_sig=None)

        # setup logger
        logger_name = 'gr_log.' + self.to_basic_block().alias()
        if logger_name in gr.logger_get_names():
            self.log = gr.logger(logger_name)
        else:
            self.log = gr.logger('log')

        self.parent = parent
        print(self.parent)
        self.usrp_id = usrp_id
        self.verbose = verbose
        self.usrp = None
        self.locked = False

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.msg_handler)


    def start(self):
        self.log.debug("Starting NTP/PPS Time Sync")

        '''
        Overload start function
        '''
        try:
            # Check to ensure
            self.usrp = eval("self.parent.%s"%self.usrp_id)
            if self.verbose: print(self.usrp)

            # Check if we have a GPSDO
            names = self.usrp.get_mboard_sensor_names()
            if self.verbose: print(names)
            if 'gps_time' in names:
                self.has_gpsdo = True
                self.log.debug("You have a GPSDO...There are better ways to sync than this block.")


        except AttributeError:
            self.log.error("Unable to acquire usrp object for synchronization")
            return True

        except Exception as e:
            self.log.error(repr(e))

        # synchronize
        self.synchronize()

        # if not locked, default time to current system time
        if not self.locked:
            try:
                self.log.debug("USRP GPS Time Sync: Defaulting to Current System Time")
                self.usrp.set_time_now(uhd.time_spec_t(time.time()))
            except Exception as e:
                self.log.error("Set Time Next PPS Error: " + repr(e))
        return True

    def synchronize(self):
        '''
        0. Stop USRP.
        1. Get USRP Sensors, mainly checking for PPS input.
        2. Poll PPS for input.
        3. on PPS event, get current PC Time (aka Wall Clock, assumes locked with NTP)
           Assume the wall clock is hapening AFTER the PPS...expect milliseconds
        4. Round up Wall Clock time to the next second rollover, 0 fractional seconds
        5. On next PPS event, set USRP time.
        6. Some kind of time check.....maybe compare next PPS with current USRP time.
        7. return true/false...if not true set usrp time to current system time (with ntp level slop)
        8. restart USRP.
        '''

        # check usrp object, if none return and set time with NTP slop
        if (self.usrp == None):
            return False

        # stop first
        self.usrp.stop()
        self.log.debug("USRP Object Stopped for Time Synchronization")

        t_now_usrp = self.usrp.get_time_now()
        t_last_pps_usrp = self.usrp.get_time_last_pps()
        print("usrp_now", t_now_usrp.get_full_secs(), t_now_usrp.get_frac_secs())
        print("lasp_pps",t_last_pps_usrp.get_full_secs(), t_last_pps_usrp.get_frac_secs())

        # set start time in future
        #self.usrp.set_start_time(uhd.time_spec_t(gps_seconds+2.0))
        self.log.debug("Starting USRP in 2 Seconds")
        time.sleep(2)

        # restart
        self.usrp.start()
        self.log.debug("USRP Objected Restarted After Time Synchronization")


    def msg_handler(self,p):
        print(p)

    def work(self, input_items, output_items):
        pass
