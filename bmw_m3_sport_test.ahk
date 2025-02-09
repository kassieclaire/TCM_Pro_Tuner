#SingleInstance Force
SetWorkingDir %A_ScriptDir%

; Default starting positions:
; - Front Power Distribution: Starts at 60% (right to decrease)
; - Front Brake Balance: Starts at 80% (right to decrease)
; - All other settings: Start at 0

; Auto-skipped settings (not available for this car):
; - front_power_distrib

^!s::  ; Ctrl+Alt+S hotkey
{
    SetKeyDelay, 50, 50  ; Adjust timing if needed

    ; Adjusting front_brake_balance (from 80%)
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
    ; Adjusting spring_front
    Send {Down}
    Send {Right}
    ; Adjusting spring_rear
    Send {Down}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    ; Adjusting compression_front
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
    ; Adjusting compression_rear
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Left}
    ; Adjusting rebound_front
    Send {Down}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    Send {Right}
    ; Adjusting rebound_rear
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