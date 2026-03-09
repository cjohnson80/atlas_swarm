#!/bin/bash
export PATH=~/.npm-global/bin:$PATH
pm2 stop all
pm2 delete all
