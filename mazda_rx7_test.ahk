#SingleInstance Force
SetWorkingDir %A_ScriptDir%

; Default starting positions:
; - Front Power Distribution: Starts at 60% (right to decrease)
; - Front Brake Balance: Starts at 80% (right to decrease)
; - All other settings: Start at 0

; Auto-skipped settings (not available for this car):

^!s::  ; Ctrl+Alt+S hotkey
{
    SetKeyDelay, 50, 50  ; Adjust timing if needed

    ; Adjusting front_power_distrib (from 60%)
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    ; Adjusting front_brake_balance (from 80%)
    Send {Down}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    ; Adjusting load_rear
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    ; Adjusting spring_front
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    ; Adjusting spring_rear
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    ; Adjusting compression_front
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    ; Adjusting compression_rear
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    ; Adjusting rebound_front
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    ; Adjusting rebound_rear
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    ; Adjusting arb_front
    Send {Down}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    ; Adjusting arb_rear
    Send {Down}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    ; Adjusting camber_front
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    ; Adjusting camber_rear
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}

    MsgBox, Settings applied!
    return
}