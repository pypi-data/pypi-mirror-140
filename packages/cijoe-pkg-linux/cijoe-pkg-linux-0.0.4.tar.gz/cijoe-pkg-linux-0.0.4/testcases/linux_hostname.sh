#!/usr/bin/env bash
#
# Basic testcase doing nothing but invoke 'hostname'
#
# The testcase itself is not intended to show anything, the interesting part is seeing what happens
# with the hooks added to the testplan
#
# shellcheck disable=SC2119
#
CIJ_TEST_NAME=$(basename "${BASH_SOURCE[0]}")
export CIJ_TEST_NAME
# shellcheck source=modules/cijoe.sh
source "$CIJ_ROOT/modules/cijoe.sh"
test.enter

if ! cij.cmd "hostname"; then
  test.fail "Failed running 'hostname' on test-target"
fi

test.pass
