#!/bin/bash

# The Django project directory
PROJECT_DIR="/home/app/medical_p"
# Screen session name
SESSION_NAME="django_app"

if ! command -v screen &>/dev/null; then
    echo "The 'screen' command is not installed."
    echo "You can install it with 'sudo apt install screen' on Ubuntu/Debian, or 'sudo yum install screen' on CentOS/RHEL."
    exit 1
fi

is_running() {
    screen -list | grep -q "$SESSION_NAME"
}

start_program() {
    if is_running; then
        echo "The Django application is already running."
    else
        echo "Starting Django application..."
        # This will start the screen session as root
        cd $PROJECT_DIR && screen -Sdm $SESSION_NAME bash -c "uv run python manage.py runserver 0.0.0.0:80"
        echo "The Django application has been started."
    fi
}

stop_program() {
    if is_running; then
        screen -S $SESSION_NAME -X quit
        echo "The Django application has been stopped."
    else
        echo "The Django application is not running."
    fi
}

attach_program() {
    if is_running; then
        echo "You are about to attach to the Django application's screen session."
        echo "To detach without stopping the application, press Ctrl-a followed by d."
        read -p "Do you want to continue? (y/n) " confirm
        if [[ $confirm == [Yy]* ]]; then
            screen -r $SESSION_NAME
        else
            echo "Operation cancelled."
        fi
    else
        echo "The Django application is not running."
    fi
}

if [ $# -eq 0 ]; then
    while true; do
        echo "-----------------------------"
        echo "1. Start Django Application"
        echo "2. Stop Django Application"
        echo "3. Attach to Django Application"
        echo "4. Exit"
        echo "-----------------------------"
        read -p "Enter your choice: " choice

        case $choice in
        1) start_program ;;
        2) stop_program ;;
        3) attach_program ;;
        4) break ;;
        *) echo "Invalid choice. Please enter 1, 2, 3, or 4." ;;
        esac

        echo ""
    done
else
    case $1 in
    start) start_program ;;
    stop) stop_program ;;
    attach) attach_program ;;
    *) echo "Usage: $0 {start|stop|attach}" ;;
    esac
fi
