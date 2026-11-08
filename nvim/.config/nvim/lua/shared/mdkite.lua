return {
    "selimacerbas/mdkite.nvim",
    dependencies = { "selimacerbas/kitehost.nvim" },
    cmd = "MdKite",
    config = function()
        -- Loopback-only; reach it from the laptop with ssh -L 8686:127.0.0.1:8686.
        require("mdkite").setup({
            host = "127.0.0.1",
            port = 8686,
            open_browser = false,
            hooks = { on_start = function(url) vim.notify("mdkite: " .. url) end },
        })
    end,
}
