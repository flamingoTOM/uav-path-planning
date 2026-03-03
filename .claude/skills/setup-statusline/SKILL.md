---
name: setup-statusline
description: 配置 Claude Code 状态栏。支持7种组件：模型名称、上下文进度条、Token统计、Momenta余额(可选)、Git分支、当前目录、运行时长。用户可自定义选择组件和显示顺序。只有选择Momenta余额时才需要提供凭据。生成动态脚本~/.claude/statusline-command.sh并更新settings.json。【重要】Momenta API使用Authorization:${TOKEN}(不是Bearer)，自动兼容两种响应格式(.data.key.spend和.spend)。Runtime会话检测使用混合机制(终端环境变量WT_SESSION/WINDOWID/TMUX_PANE + session_id)，支持Windows/Linux/tmux多终端独立计时，新终端或/clear命令后自动重置。
author: "Yannan Guo"
---

# Setup Statusline Skill

Configure Claude Code statusline with customizable components.


## When to Use This Skill

配置 Claude Code 状态栏。支持7种组件：模型名称、上下文进度条、Token统计、Momenta余额(可选)、Git分支、当前目录、运行时长。用户可自定义选择组件和显示顺序。只有选择Momenta余额时才需要提供凭据。生成动态脚本~/.claude/statusline-command.sh并更新settings.json。【重要】Momenta API使用Authorization:${TOKEN}(不是Bearer)，自动兼容两种响应格式(.data.key.spend和.spend)。Runtime会话检测使用混合机制(终端环境变量WT_SESSION/WINDOWID/TMUX_PANE + session_id)，支持Windows/Linux/tmux多终端独立计时，新终端或/clear命令后自动重置。

## Trigger

When user says:
- "setup statusline"
- "configure statusline"
- "install statusline"

## Customization Flow

**IMPORTANT**: Always show user available options and let them customize before setup.

### Available Components

1. **Model Name** - Display current Claude model (e.g., `[Sonnet 4]`)
2. **Context Bar** - Visual progress bar of context usage (e.g., `███░░░░░░░ 30%`)
3. **Token Stats** - Input/Output token counts (e.g., `⬇ 59,172 ⬆ 3,200`)
4. **Momenta Balance** - API usage and budget (e.g., `? 249/800(31.2%)`)
5. **Git Branch** - Current git branch name (e.g., `main`)
6. **Current Directory** - Current working directory (e.g., `? ~/projects/myapp`)
7. **Runtime** - Session runtime duration (e.g., `? 1h 23m`)

### User Interaction Steps

#### Step 1: Show Options

Present user with customization options using AskUserQuestion:

```
Question: "Which components would you like in your statusline?"
Type: multiSelect
Options:
  1. Model Name - Shows current Claude model
  2. Context Bar - Shows context usage with progress bar
  3. Token Stats - Shows input/output token counts
  4. Momenta Balance - Shows API usage and budget (requires credentials)
  5. Git Branch - Shows current git branch
  6. Current Directory - Shows current working directory
  7. Runtime - Shows session runtime duration
```

#### Step 2: Get Order

After user selects components, ask for the order:

```
Question: "In what order should these appear?"
Type: single select (ask for each position)
Show only the selected components as options.
Default order if not specified: Model → Context → Tokens → Balance → Directory → Branch → Runtime
```

#### Step 3: Get Momenta Credentials (If Selected)

If user selected "Momenta Balance":

```
Use AskUserQuestion with two inputs:
- username (text, required)
- password (password, required)
```

If user did NOT select "Momenta Balance", skip credential questions.

## Implementation Steps

### 1. Present Customization Options

Use AskUserQuestion to let user choose components (multiSelect).

### 2. Determine Component Order

Based on user selection, determine display order:
- Either ask user to specify order
- Or use default order: Model → Context → Tokens → Balance → Branch

### 3. Get Momenta Credentials (Conditional)

Only if "Momenta Balance" was selected:
- Ask for username and password
- Otherwise skip this step

### 4. Create Scripts Directory

```bash
mkdir -p ~/.claude/scripts
```

### 5. Generate Statusline Script

**IMPORTANT**: Dynamically generate `~/.claude/statusline-command.sh` based on user selections.

Use `statusline-command.sh.template` as reference, but customize it:

**Template structure** (modify based on selections):

```bash
#!/bin/bash
input=$(cat)

# Extract data (only what's needed)
# ... extract model_name, tokens, etc based on selections

# ANSI colors
CYAN='\033[96m'
GREEN='\033[92m'
# ... other colors

# Build status line dynamically
status=""

# Add components in user-specified order
# For each selected component, append to status:

# Example: If user wants [Model, Tokens, Branch]
status+="${CYAN}[${model_name}]${RESET}"
status+=" ${GRAY}│${RESET} ${BLUE}⬇ ${total_input}${RESET}"
status+=" ${GRAY}│${RESET} ${CYAN}${branch}${RESET}"

echo -e "$status"
```

**Component code snippets**:

**Model Name**:
```bash
model_name=$(echo "$input" | jq -r '.model.display_name')
status+="${CYAN}[${model_name}]${RESET}"
```

**Context Bar**:
```bash
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
if [ -n "$used_pct" ]; then
    bar=$(get_progress_bar "$used_pct")
    color=$(get_color_by_usage "$used_pct")
    status+=" ${color}${bar} ${used_pct}%${RESET}"
fi
# Requires: get_progress_bar() and get_color_by_usage() functions
```

**Token Stats**:
```bash
total_input=$(echo "$input" | jq -r '.context_window.total_input_tokens')
total_output=$(echo "$input" | jq -r '.context_window.total_output_tokens')
status+=" ${GRAY}│${RESET} ${BLUE}⬇ $(format_number $total_input)${RESET}"
status+=" ${MAGENTA}⬆ $(format_number $total_output)${RESET}"
# Requires: format_number() function
```

**Momenta Balance**:
```bash
if [ -f "$HOME/.claude/scripts/check-momenta-token.sh" ]; then
    token_balance=$(timeout 2s bash "$HOME/.claude/scripts/check-momenta-token.sh" 2>/dev/null || echo "")
    if [ -n "$token_balance" ]; then
        status+=" ${GRAY}│${RESET} ${YELLOW}? ${token_balance}${RESET}"
    fi
fi
```

**Git Branch**:
```bash
cwd=$(echo "$input" | jq -r '.workspace.current_dir')
if [ -d "$cwd/.git" ] || git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null || echo "detached")
    status+=" ${GRAY}│${RESET} ${CYAN}${branch}${RESET}"
fi
```

**Current Directory**:
```bash
cwd=$(echo "$input" | jq -r '.workspace.current_dir')
# Show shortened path: replace $HOME with ~
short_path="${cwd/#$HOME/\~}"
# Or show only directory name: basename
dir_name=$(basename "$cwd")
# Choose one:
status+=" ${GRAY}│${RESET} ${BLUE}? ${short_path}${RESET}"
# Or: status+=" ${GRAY}│${RESET} ${BLUE}? ${dir_name}${RESET}"
```

**Runtime**:
```bash
# Normalize path for consistent hashing (convert to lowercase)
cwd=$(echo "$input" | jq -r '.workspace.current_dir')
normalized_cwd=$(echo "$cwd" | tr '[:upper:]' '[:lower:]')
PROJECT_HASH=$(echo "$normalized_cwd" | md5sum 2>/dev/null | cut -d' ' -f1 || echo "unknown")

# Hybrid session detection: Terminal ID + session_id
# Try terminal-specific env vars (ordered by popularity):
# 1. WT_SESSION (Windows Terminal) 2. WINDOWID (X11/Linux) 3. TMUX_PANE (tmux)
# session_id: precise detection for /clear command
TERMINAL_ID=$(echo "${WT_SESSION:-${WINDOWID:-${TMUX_PANE:-fallback_$$}}}" | md5sum 2>/dev/null | cut -d' ' -f1 | cut -c1-8)
RUNTIME_FILE="$HOME/.claude/runtime_${PROJECT_HASH}_${TERMINAL_ID}_start"
SESSION_FILE="$HOME/.claude/runtime_${PROJECT_HASH}_${TERMINAL_ID}_session"

current_time=$(date +%s)

# Get current session_id from history.jsonl
current_session=$(tail -1 "$HOME/.claude/history.jsonl" 2>/dev/null | jq -r '.sessionId // empty')

if [ -n "$current_session" ]; then
    last_session=$(cat "$SESSION_FILE" 2>/dev/null || echo "")

    # If session_id changed → new session (e.g., /clear) → reset timer
    if [ "$current_session" != "$last_session" ]; then
        echo "$current_time" > "$RUNTIME_FILE"
        echo "$current_session" > "$SESSION_FILE"
    fi
else
    # Fallback: if can't read session_id, use file existence (new terminal)
    if [ ! -f "$RUNTIME_FILE" ]; then
        echo "$current_time" > "$RUNTIME_FILE"
    fi
fi

start_time=$(cat "$RUNTIME_FILE" 2>/dev/null || echo "$current_time")
runtime=$((current_time - start_time))

# Format: hours, minutes, or seconds
hours=$((runtime / 3600))
minutes=$(((runtime % 3600) / 60))
seconds=$((runtime % 60))

if [ $hours -gt 0 ]; then
    runtime_str="${hours}h ${minutes}m"
elif [ $minutes -gt 0 ]; then
    runtime_str="${minutes}m"
else
    runtime_str="${seconds}s"
fi
status+=" ${GRAY}│${RESET} ${MAGENTA}? ${runtime_str}${RESET}"
```

**Required Helper Functions** (include if needed):

```bash
# Format numbers with comma separator (for Token Stats)
format_number() {
    printf "%'d" "$1" 2>/dev/null || echo "$1"
}

# Get progress bar (for Context Bar)
get_progress_bar() {
    local pct=$1
    local width=10
    local filled=$((pct * width / 100))
    local empty=$((width - filled))
    local bar=""
    for ((i=0; i<filled; i++)); do bar+="█"; done
    for ((i=0; i<empty; i++)); do bar+="░"; done
    echo "$bar"
}

# Get color by usage (for Context Bar)
get_color_by_usage() {
    local pct=$1
    if [ "$pct" -lt 50 ]; then echo -e "$GREEN"
    elif [ "$pct" -lt 75 ]; then echo -e "$YELLOW"
    else echo -e "$RED"; fi
}
```

### 6. Create Balance Checker (Conditional)

Only if "Momenta Balance" was selected:

Copy from `check-momenta-token.sh.template` to `~/.claude/scripts/check-momenta-token.sh`

Replace placeholders:
- `{{USERNAME}}` → user's username
- `{{PASSWORD}}` → user's password

If "Momenta Balance" was NOT selected, skip this step entirely.

### 7. Make Executable

```bash
chmod +x ~/.claude/statusline-command.sh
# Only if Momenta Balance selected:
[ -f ~/.claude/scripts/check-momenta-token.sh ] && chmod +x ~/.claude/scripts/check-momenta-token.sh
```

### 8. Update Settings

Update or create `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline-command.sh"
  }
}
```

If file exists: read it, preserve existing settings, add/update statusLine section.

### 9. Test Configuration

Test the generated statusline script with sample input:

```bash
echo '{"model":{"display_name":"Test"},"context_window":{"total_input_tokens":1000,"total_output_tokens":200,"used_percentage":10},"workspace":{"current_dir":"'$(pwd)'"}}' | bash ~/.claude/statusline-command.sh
```

Show the output to user as a preview.

### 10. Save Credentials (Conditional)

Only if Momenta Balance was selected, optionally create backup config:

```json
{
  "username": "provided-username",
  "password": "provided-password",
  "api_base": "https://abp.momenta.works",
  "api_endpoint": "/mdify/api/v1/api-key"
}
```

Save to `~/.claude/momenta-config.json` with `chmod 600`.

### 11. Inform User

Tell user:
- ✅ Statusline configured with selected components: [list them]
- Display order: [show order]
- Show preview of statusline output
- May need to restart Claude Code

## Example Configurations

### Example 1: Minimal (Model + Branch)

User selects: Model Name, Git Branch

Result:
```
[Sonnet 4] │ main
```

### Example 2: Full Setup (All Components)

User selects: All 7 components
Order: Model → Context → Tokens → Balance → Directory → Branch → Runtime

Result:
```
[Sonnet 4] ███░░░░░░░ 30% │ ⬇ 59,172 ⬆ 3,200 │ ? 249/800(31.2%) │ ? ~/projects │ main │ ? 1h 23m
```

### Example 3: Developer Focus

User selects: Model, Current Directory, Git Branch, Runtime
Order: Model → Directory → Branch → Runtime

Result:
```
[Sonnet 4] │ ? ~/projects/myapp │ main │ ? 1h 23m
```

### Example 4: Budget Focus

User selects: Model, Momenta Balance, Tokens
Order: Model → Balance → Tokens

Result:
```
[Sonnet 4] │ ? 249/800(31.2%) │ ⬇ 59,172 ⬆ 3,200
```

## Technical Details

### Component Details

**Model Name**:
- Color: Cyan
- Example: `[Sonnet 4]`, `[Opus 4.6]`

**Context Bar**:
- Colors: Green (<50%), Yellow (50-75%), Red (>75%)
- Format: `████░░░░░░ 30%`
- Width: 10 characters

**Token Stats**:
- Input: Blue with ⬇ symbol
- Output: Magenta with ⬆ symbol
- Format: Comma-separated thousands (e.g., `59,172`)

**Momenta Balance**:
- Color: Yellow
- Format: `? spent/total(percentage%)`
- Example: `? 249/800(31.2%)`
- Cache: 10 minutes
- Timeout: 2 seconds

**Git Branch**:
- Color: Cyan
- Shows current branch name
- Falls back to "detached" if not on a branch

**Current Directory**:
- Color: Blue
- Format: `? ~/path/to/dir` or `? dirname`
- Shows current working directory
- Can display full path (with ~ for $HOME) or just directory name

**Runtime**:
- Color: Magenta
- Format: `? 1h 23m`, `? 45m`, or `? 30s`
- Shows session duration since start
- Automatically selects unit: seconds (< 1m), minutes (< 1h), or hours+minutes
- **Session Detection Mechanism (Hybrid: Terminal ID + session_id)**:
  - ✅ Each Claude Code session gets its own independent timer
  - ✅ Multi-platform terminal detection + session_id tracking
  - ✅ Works on Windows Terminal, X11 terminals, tmux, and standard shells
  - ✅ Automatically resets on new terminal or `/clear` command
- How it works:
  1. Generates `TERMINAL_ID` from terminal-specific environment variables (tries in order):
     - `WT_SESSION` - Windows Terminal (unique per tab)
     - `WINDOWID` - X11 terminals on Linux (gnome-terminal, xterm, etc.)
     - `TMUX_PANE` - tmux sessions (unique per pane)
     - `$$` - Process ID fallback (for other shells)
  2. Reads current `sessionId` from `~/.claude/history.jsonl` (last line)
  3. Compares with stored session_id in `~/.claude/runtime_${PROJECT_HASH}_${TERMINAL_ID}_session`
  4. If session_id changed → new session (e.g., `/clear`) → reset timer and store new session_id
  5. If session_id unchanged → same session → continue counting
  6. Fallback: if history.jsonl unreadable, uses file existence check (new terminal detection)
- Session resets when:
  - New terminal window/tab opens (detected via WT_SESSION change)
  - User runs `/clear` command (detected via session_id change)
  - Claude Code process restarts
- Path normalization:
  - Converts path to lowercase to handle Windows path format inconsistencies
  - `C:\Users\...` and `/c/Users/...` generate the same PROJECT_HASH
- Runtime tracking files:
  - Start time: `~/.claude/runtime_${PROJECT_HASH}_${TERMINAL_ID}_start` (Unix epoch timestamp)
  - Session ID: `~/.claude/runtime_${PROJECT_HASH}_${TERMINAL_ID}_session` (current sessionId)
  - Example: `~/.claude/runtime_d25605a8a19bf0faf5d14bd650f0e1c1_a1b2c3d4_start`
  - TERMINAL_ID is first 8 chars of md5 hash of WT_SESSION (or fallback_$$)
- Behavior:
  - Same session can run for hours without resetting
  - Long thinking time doesn't affect timer (still same session_id)
  - Each new terminal/clear gets fresh timer automatically
  - Multiple terminal tabs maintain independent timers
- To reset manually: `rm ~/.claude/runtime_*`

### Momenta API

**Only needed if Balance component selected**:

**Login**:
- URL: `https://abp.momenta.works/auth/api/v1/user/login`
- Method: POST
- Content-Type: `application/x-www-form-urlencoded`
- Body: `username=XXX&password=YYY`

**Get Balance**:
- URL: `https://abp.momenta.works/mdify/api/v1/api-key`
- Method: GET
- Header: `Authorization: ${TOKEN}` (NOT "Bearer ${TOKEN}")

**Response Format Compatibility**:
The balance checker supports both API response formats:
- **Windows format** (nested): `{"data":{"key":{"spend":283.7,"max_budget":800}}}`
- **Linux format** (flat): `{"spend":283.7,"max_budget":800}`

The script automatically detects the format and extracts the correct values.

**Token Cache**:
- Location: `/tmp/momenta_token_cache`
- Duration: 10 minutes

### Separator

Always use: `${GRAY}│${RESET}` between components for consistent styling.

## Files Created

**Always**:
- `~/.claude/statusline-command.sh` - Customized statusline script
- `~/.claude/settings.json` - Updated with statusLine config

**Conditional** (only if Momenta Balance selected):
- `~/.claude/scripts/check-momenta-token.sh` - Balance checker with credentials
- `~/.claude/momenta-config.json` - Credentials backup (optional)
- `/tmp/momenta_token_cache` - Token cache (temporary)

**Runtime** (only if Runtime component selected):
- `~/.claude/runtime_${PROJECT_HASH}_${TERMINAL_ID}_start` - Session start timestamp files (per project + terminal)
- `~/.claude/runtime_${PROJECT_HASH}_${TERMINAL_ID}_session` - Session ID tracking files (per project + terminal)
- Note: Each terminal tab maintains independent runtime tracking via TERMINAL_ID

## Error Handling

**If component fails**:
- Skip that component silently
- Continue with other components
- Statusline still works

**If no components selected**:
- Ask user to select at least one component
- Suggest default: Model + Context + Tokens

**Security**:
- Credentials stored in plain text (if Momenta selected)
- Recommend: `chmod 600` on credential files
