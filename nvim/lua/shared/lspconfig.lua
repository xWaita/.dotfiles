-- vim.lsp.buf.code_action() is asynchronous, so there will be a race condition when saving
-- we could do a vim.wait() after vim.lsp.buf.code_action(), but that's ew and hacky
-- therefore we use our own synchronous sorting function
function sort_import_sync()
    -- timeout defaults to 1000 but this may be too short depending on machine and codebase size
    local timeout = 1000
    -- TODO: detect offset encoding from lsp client
    local offset_encoding = 'utf-16'

    local params = vim.lsp.util.make_range_params()
    params.context = { 
        diagnostics = {}, 
        triggerKind = vim.lsp.protocol.CodeActionTriggerKind.Invoked, 
        only = { 'source.organizeImports' },
    }
    local result = vim.lsp.buf_request_sync(0, 'textDocument/codeAction', params, timeout)

    for _, res in pairs(result or {}) do
        for _,r in pairs(res.result or {}) do
            if r.edit then
                vim.lsp.util.apply_workspace_edit(r.edit, offset_encoding)
            else
                vim.lsp.buf.execute_command(r.command)
            end
        end
    end
end

return {
    'neovim/nvim-lspconfig',
    config = function()
        local lspconfig = require('lspconfig')
        lspconfig.rust_analyzer.setup {}
        -- if ruff-lsp isn't respecting ruff.toml, implement the following:
        -- https://github.com/hahuang65/nvim-config/blob/main/lua/plugins/lsp.lua#L91
        lspconfig.ruff_lsp.setup {}
        lspconfig.pyright.setup {}

        -- LspAttach maps keys after the lsp attaches to the current buffer
        vim.api.nvim_create_autocmd('LspAttach', {
            group = vim.api.nvim_create_augroup('UserLspConfig', {}),
            callback = function(ev)

                -- auto format and sort imports using the attached lsp on save
                vim.api.nvim_create_autocmd('BufWritePre', {
                    group = vim.api.nvim_create_augroup('AutoFormatting', {}),
                    callback = function()
                        vim.lsp.buf.format()
                        sort_import_sync()
                    end
                })

                -- Buffer local mappings.
                -- See `:help vim.lsp.*` for documentation on any of the below functions
                local opts = { buffer = ev.buf }
                vim.keymap.set('n', 'gD', vim.lsp.buf.declaration, opts)
                vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)
                vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
                vim.keymap.set('n', 'gi', vim.lsp.buf.implementation, opts)
                vim.keymap.set('n', '<C-k>', vim.lsp.buf.signature_help, opts)
                vim.keymap.set('n', '<space>wa', vim.lsp.buf.add_workspace_folder, opts)
                vim.keymap.set('n', '<space>wr', vim.lsp.buf.remove_workspace_folder, opts)
                vim.keymap.set('n', '<space>wl', function()
                    print(vim.inspect(vim.lsp.buf.list_workspace_folders()))
                end, opts)
                vim.keymap.set('n', '<space>D', vim.lsp.buf.type_definition, opts)
                vim.keymap.set('n', '<space>rn', vim.lsp.buf.rename, opts)
                vim.keymap.set({ 'n', 'v' }, '<space>ca', vim.lsp.buf.code_action, opts)
                vim.keymap.set('n', 'gr', vim.lsp.buf.references, opts)
                vim.keymap.set('n', '<space>l', function()
                    vim.lsp.buf.format { async = true }
                end, opts)
                vim.keymap.set('n', '<space>e', vim.diagnostic.open_float, opts)
            end,
        })
    end,
}
