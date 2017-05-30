#!/bin/bash


supervisord

echo "start supervisord"

tail -f /dev/null