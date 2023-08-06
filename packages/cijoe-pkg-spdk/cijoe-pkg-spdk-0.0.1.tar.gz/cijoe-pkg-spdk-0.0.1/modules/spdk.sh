#!/usr/bin/env bash
#
# CIJOE module to verify environment variables for SPDK testcases
#
# For documentation of parameters / variables.
#
# spdk.env    - Checks environment for module parameters
# spdk.fioe   - Runs fio with the xNVMe fio IO Engine
#
spdk.env() {
  if [[ ! -v SPDK_REPOS ]]; then
    cij.err "missing definition of SPDK_REPOS"
    return 1
  fi

  return 0
}
