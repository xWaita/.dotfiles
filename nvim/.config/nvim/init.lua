-- must be set before plugins
vim.g.mapleader = ' '
vim.g.maplocalleader = ' '
vim.g.loaded_netrw = 1       -- disable for nvim-tree
vim.g.loaded_netrwPlugin = 1 -- disable for nvim-tree

-- lazy.nvim install
local lazypath = vim.fn.stdpath('data') .. '/lazy/lazy.nvim'
if not vim.loop.fs_stat(lazypath) then
    vim.fn.system({
        'git',
        'clone',
        '--filter=blob:none',
        'https://github.com/folke/lazy.nvim.git',
        '--branch=stable',
        lazypath,
    })
end
vim.opt.rtp:prepend(lazypath)

-- load plugins
local plugins = {
    { 'neovim/nvim-lspconfig' },
    { 'f-person/git-blame.nvim' },
    { 'chrisbra/csv.vim' },

    { import = 'shared' }, -- import all plugins from lua/plugins
    { import = 'home' },   -- home specific plugins
    { import = 'tibra' },  -- tibra specific plugins
}
require('lazy').setup(plugins, opts)

-- swap jumplist commands
vim.keymap.set('n', '<c-i>', '<c-o>', {})
vim.keymap.set('n', '<c-o>', '<c-i>', {})

-- swap high and low
vim.keymap.set('n', 'H', 'L', {})
vim.keymap.set('v', 'H', 'L', {})
vim.keymap.set('n', 'L', 'H', {})
vim.keymap.set('v', 'L', 'H', {})

-- nvim options
vim.cmd.colorscheme 'catppuccin'
vim.opt.clipboard = 'unnamedplus'
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.expandtab = true
vim.opt.relativenumber = true
vim.opt.number = true
vim.opt.termguicolors = true

-- remote/terminal: OSC52 for copy (reaches the host system clipboard over SSH).
-- Paste reads nvim's own register instead of querying the terminal — OSC52 paste
-- makes nvim wait for a terminal reply that Zed never sends, causing the
-- "waiting for OSC 52 response" freeze on every paste.
if vim.env.SSH_TTY or vim.env.SSH_CONNECTION then
    local function paste()
        return {
            vim.fn.split(vim.fn.getreg(""), "\n"),
            vim.fn.getregtype(""),
        }
    end
    vim.g.clipboard = {
        name = "OSC52",
        copy = {
            ["+"] = require("vim.ui.clipboard.osc52").copy("+"),
            ["*"] = require("vim.ui.clipboard.osc52").copy("*"),
        },
        paste = {
            ["+"] = paste,
            ["*"] = paste,
        },
    }
end
-- jupyter: allow shift+mouse copying
vim.keymap.set("n", "<leader>cc", function()
    vim.opt.number = false
    vim.opt.relativenumber = false
    vim.opt.signcolumn = "no"
    vim.opt.mouse = ""
end)
