#SingleInstance Force
SetWorkingDir %A_ScriptDir%

^!s::
{
    SetKeyDelay, 50, 50  ; Adjust timing if needed

    ; Adjusting front_brake_balance
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