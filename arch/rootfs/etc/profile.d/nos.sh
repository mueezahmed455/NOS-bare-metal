# NeuralOS Environment Profile
# /etc/profile.d/nos.sh

export PYTHONPATH="/usr/lib/nos:${PYTHONPATH}"
export NOS_VERSION="0.1.0"
export NOS_SHELL="/usr/bin/nos-shell"

# NeuralOS aliases
alias nos='python3 /usr/bin/nos'
alias nos-status='python3 /usr/bin/nos status'
alias nos-diagnose='python3 /usr/bin/nos diagnose'
alias nos-memory='python3 /usr/bin/nos memory'
alias nos-cache='python3 /usr/bin/nos cache'

# Prompt customization
if [ -n "$BASH_VERSION" ]; then
    PS1='\[\e[1;36m\]\u@\h\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\] [\[\e[1;33m\]neurlos\[\e[0m\]]\nλ '
fi
