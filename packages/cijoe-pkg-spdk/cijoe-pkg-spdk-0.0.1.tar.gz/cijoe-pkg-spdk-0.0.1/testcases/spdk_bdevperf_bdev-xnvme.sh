#!/bin/bash
#
# Verify that 'bdevperf' runs using the bdev-configuration at SPDK_BDEV_CONFIG
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

: "${XNVME_ASYNC:?Must be set and non-empty}"

cij.info "Using bdev-configuration:"
if ! cij.cmd "cat ${SPDK_BDEV_CONFIG}"; then
  test.fail
fi

if ! cij.cmd "${SPDK_REPOS}/test/bdev/bdevperf/bdevperf -c ${SPDK_BDEV_CONFIG} -q 16 -o 4096 -w verify -t 20"; then
  test.fail "failing running 'bdevperf'"
fi

test.pass
