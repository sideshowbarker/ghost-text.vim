import os
import vim
import time
import json
import ghost_log
import single_server
import vim_websocket_handler


def start_server():
    single_server.start_server()
    for _ in range(3):
        time.sleep(.1)
        vim.command("let g:channel = ch_open('localhost:4002')")
        if vim.eval('ch_status(g:channel)') == "open":
            ghost_log.p('GhostText for vim started')
            return
        ghost_log.p('could not open channel to localhost:4002, retry...')

    ghost_log.p('fail to start GhostText for vim')


def stop_server():
    if vim.eval('ch_status(g:channel)') == "open":
        vim.command('call ch_close(g:channel)')
    single_server.stop_server()


def text_changed_from_vim():
    name = os.path.basename(vim.current.buffer.name)
    if not name.startswith("GhostText"):
        return

    text = '\n'.join(vim.current.buffer)
    # vim.command()
    selections = [{'start': 1, 'end': 1}]
    json_dict = json.dumps(
        {
            'buf_name': name,
            'text': text,
            'selections': selections
        }
    )
    cmd = ':call ch_sendraw(g:channel,{})'.format(
        json.dumps(json_dict))

    vim.command(cmd)


def update_text(name, lines, selections):
    # todo : if current buffer is not the `name`d buffer, switch it
    vim.command(':b ' + name)
    mode = vim.eval('mode()')
    if not mode == 'n':
        ghost_log.p('mode', mode)
        vim.command('call feedkeys("\<esc>")')
        vim.command(":redraw")
    vim.current.buffer[:] = lines.split('\n')
    vim.command(":redraw")
    vim.command(":call cursor({})".format(selections))
