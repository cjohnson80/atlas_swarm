#!/bin/bash
export PATH=~/.npm-global/bin:$PATH
pm2 start /home/chrisj/atlas_agents/ecosystem.config.js
pm2 status
