#!/bin/bash

SESSION="workmate"
WINDOW0="ConsoleLogs"
WINDOW1="Shells"
PATH_WORKMATE="/home/einfachnurphu/Dokumente/PhuDev/workmate"

tmux new-session -d -s $SESSION -c $PATH_WORKMATE/backend -n $WINDOW0

# Fenster 0: ConsoleLogs
tmux send-keys -t $SESSION:0.0 "echo 'Backend Log'" C-m
tmux select-pane -t Backend_Log
tmux split-window -h -t $SESSION:0 -c $PATH_WORKMATE/ui
tmux send-keys -t $SESSION:0.1 "echo 'UI Log'" C-m
tmux select-pane -t UI_Log

# Fenster 1: Shells
tmux new-window -t $SESSION:1 -n $WINDOW1 -c $PATH_WORKMATE/backend
tmux send-keys -t $SESSION:1.0 "echo 'Backend Shell'" C-m
tmux select-pane -t Backend_Shell
tmux split-window -h -t $SESSION:1 -c $PATH_WORKMATE/ui
tmux send-keys -t $SESSION:1.1 "echo 'UI Shell'" C-m
tmux select-pane -t UI_Shell

tmux select-window -t $SESSION:0
tmux attach-session -t $SESSION