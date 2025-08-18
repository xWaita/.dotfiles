return {
    "mason-org/mason-lspconfig.nvim",
    opts = {
        ensure_installed = {
            -- if ruff-lsp isn't respecting ruff.toml, implement the following:
            -- https://github.com/hahuang65/nvim-config/blob/main/lua/plugins/lsp.lua#L91
            'ruff',
            'pyright',
            'rust_analyzer',
            'lua_ls',
        }
    },
    dependencies = {
        { "mason-org/mason.nvim", opts = {} },
        "neovim/nvim-lspconfig",
    },
}
