tmux new-session -d -s Shepherd -n Shepherd
tmux send-keys -t '=Shepherd:0' 'cd shepherd' Enter
tmux split-window -h -t '=Shepherd:0'
tmux split-window -h -t '=Shepherd:0'
tmux split-window -v -t '=Shepherd:0'
tmux split-window -v -t '=Shepherd:0.1'
tmux split-window -v -t '=Shepherd:0.0'
tmux send-keys -t 'Shepherd:0.0' 'cd shepherd' Enter
tmux send-keys -t 'Shepherd:0.1' 'cd shepherd' Enter
tmux send-keys -t 'Shepherd:0.2' 'cd shepherd' Enter
tmux send-keys -t 'Shepherd:0.3' 'cd shepherd' Enter
tmux send-keys -t 'Shepherd:0.4' 'cd shepherd' Enter
tmux send-keys -t 'Shepherd:0.5' 'cd shepherd' Enter

tmux send-keys -t 'Shepherd:0.0' 'python3 shepherd.py' Enter
tmux send-keys -t 'Shepherd:0.1' 'echo free terminal' Enter
tmux send-keys -t 'Shepherd:0.2' 'python3 server.py' Enter
tmux send-keys -t 'Shepherd:0.3' 'echo free terminal' Enter
tmux send-keys -t 'Shepherd:0.4' 'python3 sensors_config.py' Enter
tmux send-keys -t 'Shepherd:0.5' 'python3 -m ydl' Enter

tmux attach-session -t '=Shepherd'
