#!/bin/bash
#
# Verify that 'fio' runs using bdev/xNVMe using I/O interface selected by 'XNVME_ASYNC' evar.
#
# In the environment / testplan define the io-interface to use:
#
# XNVME_ASYNC={io_uring,io_uring_cmd,libaio,emu,thrpool}
#
# It uses the script 'spdk_bdevconf_create.py' to create a bdev-configuration
#
# shellcheck disable=SC2119
#
CIJ_TEST_NAME=$(basename "${BASH_SOURCE[0]}")
export CIJ_TEST_NAME
# shellcheck source=modules/cijoe.sh
source "$CIJ_ROOT/modules/cijoe.sh"
test.enter

cij.info "Using bdev-configuration:"
if ! cij.cmd "cat ${SPDK_BDEV_CONFIG}"; then
  test.fail
fi

FIO_ARGS=""
FIO_ARGS="${FIO_ARGS} --ioengine=spdk_bdev"
FIO_ARGS="${FIO_ARGS} --spdk_json_conf=${SPDK_BDEV_CONFIG}"
FIO_ARGS="${FIO_ARGS} --thread=1"
FIO_ARGS="${FIO_ARGS} --group_reporting=1"
FIO_ARGS="${FIO_ARGS} --time_based=1"
FIO_ARGS="${FIO_ARGS} --runtime=10"
FIO_ARGS="${FIO_ARGS} --ramp_time=2"
FIO_ARGS="${FIO_ARGS} --iodepth=1"
FIO_ARGS="${FIO_ARGS} --direct=1"
FIO_ARGS="${FIO_ARGS} --rw=randread"
FIO_ARGS="${FIO_ARGS} --bs=${SPDK_BDEV_BS}"
FIO_ARGS="${FIO_ARGS} --name=foo42"
FIO_ARGS="${FIO_ARGS} --numjobs=1"
FIO_ARGS="${FIO_ARGS} --filename=bdev_auto"

if ! cij.cmd "LD_PRELOAD=${SPDK_REPOS}/build/fio/spdk_bdev ${FIO_BIN} ${FIO_ARGS}"; then
  test.fail "FAILED: running 'fio' using spdk_bdev/xNVMe"
fi

test.pass
