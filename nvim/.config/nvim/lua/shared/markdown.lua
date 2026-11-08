return {
    "iamcco/markdown-preview.nvim",
    cmd = { "MarkdownPreviewToggle", "MarkdownPreview", "MarkdownPreviewStop" },
    ft = { "markdown" },
    build = "cd app && npm install",
    init = function()
        -- Fixed port for the SSH LocalForward; server stays loopback-only (no open_to_the_world).
        vim.g.mkdp_port = "8686"
        vim.g.mkdp_echo_preview_url = 1
        vim.g.mkdp_auto_close = 0
    end,
}
