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

    MsgBox, Settings applied!
    return
}