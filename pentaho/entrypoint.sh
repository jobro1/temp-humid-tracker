#!/bin/bash
set -e

KETTLE_HOME="${KETTLE_HOME:-/app}"
mkdir -p "${KETTLE_HOME}/.kettle"

env | sort > "${KETTLE_HOME}/.kettle/kettle.properties"

exec /opt/pentaho/data-integration/pan.sh "$@"
