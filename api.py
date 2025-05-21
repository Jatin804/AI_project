from groq import Groq

def should_respond(text: str) -> bool:
    linux_keywords = [
    # General actions
    "build", "compile", "create", "enable", "disable", "execute", "find", "install",
    "list", "make", "open", "purge", "remove", "restart", "run", "search", "show",
    "start", "status", "stop", "uninstall", "update", "upgrade", "whereis", "which",

    # File operations
    "cat", "cd", "cp", "head", "less", "ls", "mkdir", "more", "mv", "nano",
    "pwd", "rm", "rmdir", "tail", "touch", "vi", "vim",

    # Permissions
    "chgrp", "chmod", "chown", "umask",

    # Process & system monitoring
    "df", "du", "free", "htop", "id", "kill", "killall", "nice", "ps", "renice",
    "top", "uptime", "w", "who",

    # Networking
    "curl", "dig", "ftp", "host", "ifconfig", "ip", "iwconfig", "netstat",
    "nmcli", "ping", "scp", "ssh", "ss", "telnet", "traceroute", "wget",

    # Archiving & compression
    "7z", "gzip", "gunzip", "tar", "unzip", "xz", "zip",

    # Package management (openSUSE-specific + optional tools)
    "flatpak", "snap", "zypper",

    # System management
    "journalctl", "reboot", "service", "shutdown", "systemctl",

    # Disk & partitions
    "btrfs", "blkid", "fdisk", "lsblk", "mount", "parted", "umount",

    # Shells & scripting
    "alias", "bash", "fish", "sh", "source", "tty", "zsh", "export",

    # Text processing
    "awk", "cut", "diff", "grep", "sed", "sort", "tr", "uniq", "wc",

    # Development tools
    "cmake", "docker", "g++", "gcc", "git", "kubectl", "kubernetes", "make",
    "node", "python",

    # Scheduling & system tools
    "at", "command", "crontab", "date", "shell", "terminal", "time"
    ]

            
    return any(word in text.lower() for word in linux_keywords)


def chat_with_llama(user_input: str) -> str:
    if not should_respond(user_input):
        return "Sorry, I only assist with Linux command-line usage. Please ask a related question."

    api_key = "API_KEY" 
    client = Groq(api_key=api_key)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a Linux command assistant. "
                "ONLY answer questions about Linux commands. "
                "Give output ONLY as one Linux command. "
                "Do NOT explain anything. "
                "If a user asks anything unrelated, reply: 'I can only help with Linux commands.'"
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]


    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"


# data = chat_with_llama("Open fire fox")
# print(data)