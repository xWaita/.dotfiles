return {
    'nvim-telescope/telescope.nvim',
    tag = '0.1.5',
    dependencies = { 'nvim-lua/plenary.nvim' },
    config = function()
        local telescope = require('telescope')
        local config = require("telescope.config")
        local builtin = require('telescope.builtin')

        -- Clone the default Telescope configuration
        local vimgrep_arguments = { unpack(config.values.vimgrep_arguments) }
        -- I want to search in hidden/dot files.
        table.insert(vimgrep_arguments, "--hidden")
        -- I don't want to search in the `.git` directory.
        table.insert(vimgrep_arguments, "--glob")
        table.insert(vimgrep_arguments, "!**/.git/*")

        telescope.setup({
            defaults = {
                vimgrep_arguments = vimgrep_arguments,
            },
            pickers = {
                find_files = {
                    find_command = { "rg", "--files", "--hidden", "--glob", "!**/.git/*" },
                },
            },
        })

        vim.keymap.set('n', '<leader>f', builtin.current_buffer_fuzzy_find, { desc = 'Fuzzily search in current buffer' })
        vim.keymap.set('n', '<leader>o', builtin.find_files, { desc = 'Search files' })
        vim.keymap.set('n', '<leader>g', builtin.live_grep, { desc = 'Live grep' })
        vim.keymap.set('n', '<leader>b', builtin.buffers, { desc = 'Buffers' })
    end,
}
