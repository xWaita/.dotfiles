return {
    'andythigpen/nvim-coverage',
    requires = 'nvim-lua/plenary.nvim',
    config = function()
        require('coverage').setup({
            lang = {
                coverage_file = 'cov.json'
            }
        })
    end,
}
