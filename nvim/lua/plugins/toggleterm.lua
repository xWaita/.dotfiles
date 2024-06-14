return {
    'akinsho/toggleterm.nvim', 
    config = function()
        toggleterm = require('toggleterm')
        toggleterm.setup{
            direction = 'horizontal',
            size = 90,
            insert_mappings = false,
            open_mapping = [[<A-j>]]
        }
    end,
}
