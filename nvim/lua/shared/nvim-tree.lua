return {
    'nvim-tree/nvim-tree.lua',
    requires = {
        'nvim-tree/nvim-web-devicons',
    },
    lazy = false, -- setup is very inexpensive, so there is no performance benefit to lazy load
    config = function()
        require('nvim-tree').setup { filters = { dotfiles = false, git_ignored=false } }
        local find_file_toggle = function()
            require('nvim-tree.api').tree.toggle({ find_file = true })
        end
        vim.keymap.set('n', '<leader>t', find_file_toggle, { desc = 'Toggle tree' })
    end,
}
