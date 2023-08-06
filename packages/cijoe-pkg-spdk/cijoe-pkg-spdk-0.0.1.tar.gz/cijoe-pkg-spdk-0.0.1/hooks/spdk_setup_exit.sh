#!/usr/bin/env bash
#
# Verifies that environment variables required by the SPDK testcases are
# defined and detaches / re-attaches NVMe devices from kernel to user space
#
# on-enter: de-attach from kernel NVMe driver
# on-exit: re-attach to kernel NVMe driver
#
CIJ_TEST_NAME=$(basename "${BASH_SOURCE[0]}")
export CIJ_TEST_NAME
# shellcheck source=modules/cijoe.sh
source "$CIJ_ROOT/modules/cijoe.sh"
test.enter

hook.spdk_setup_exit() {
  if ! spdk.env; then
    cij.err "spdk.env - Invalid SPDK env."
    return 1
  fi

  return 0
}

hook.spdk_setup_exit
exit $?
