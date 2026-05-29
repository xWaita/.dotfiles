-- This file will not be overwritten across dots-hyprland updates.
-- The file name is for the sake of organization and does not matter
-- See the corresponding files in ~/.config/hypr/hyprland for examples

--##! Virtual machine passthrough (ALT+V toggles; disables all keybinds)
hl.define_submap("vm", function()
    hl.bind("ALT + V", function()
        local currentsubmap = hl.get_current_submap()
        if currentsubmap == "vm" then
            hl.dispatch(hl.dsp.exec_cmd(
                "notify-send 'Exited VM submap' 'Keybinds re-enabled' -a 'Hyprland'"))
            hl.dispatch(hl.dsp.submap("reset"))
        elseif currentsubmap == "" then
            hl.dispatch(hl.dsp.exec_cmd(
                "notify-send 'Entered VM submap' 'Keybinds disabled. Hit ALT+V to escape' -a 'Hyprland'"))
            hl.dispatch(hl.dsp.submap("vm"))
        end
    end, { submap_universal = true })
end)

-- Faithful minimal alternative (silent). Comment out the block above and
-- uncomment this to use instead:
-- hl.bind("ALT + V", hl.dsp.submap("vm"))
-- hl.define_submap("vm", function()
--     hl.bind("ALT + V", hl.dsp.submap("reset"))
-- end)
