tmux new-session -d -s Shepherd -n Shepherd
tmux send-keys -t '=Shepherd:0' 'cd shepherd' Enter
tmux split-window -h -t '=Shepherd:0'
tmux split-window -h -t '=Shepherd:0'
tmux split-window -v -t '=Shepherd:0'
tmux split-window -v -t '=Shepherd:0.1'
tmux split-window -v -t '=Shepherd:0.0'
tmux send-keys -t 'Shepherd:0.0' 'cd shepherd' Enter
tmux send-keys -t 'Shepherd:0.1' 'cd shepherd' Enter
tmux send-keys -t 'Shepherd:0.2' 'cd shepherd/sensors' Enter
tmux send-keys -t 'Shepherd:0.3' 'cd shepherd' Enter
tmux send-keys -t 'Shepherd:0.4' 'cd shepherd/sensors' Enter
tmux send-keys -t 'Shepherd:0.5' 'cd shepherd' Enter

tmux send-keys -t 'Shepherd:0.0' 'python3 Shepherd.py' Enter
tmux send-keys -t 'Shepherd:0.1' 'echo free terminal' Enter
tmux send-keys -t 'Shepherd:0.3' 'python3 server.py' Enter
tmux send-keys -t 'Shepherd:0.4' 'make clean && make && ./dev_handler' Enter
tmux send-keys -t 'Shepherd:0.5' 'python3 scoreboard_server.py' Enter
tmux send-keys -t 'Shepherd:0.2' 'sleep 10' Enter
tmux send-keys -t 'Shepherd:0.2' 'python3 sensor_interface.py' Enter

tmux attach-session -t '=Shepherd'
