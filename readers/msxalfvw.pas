program G3AlfabetoViewer;

  uses CRT,Graph;

  type
    BinFT = file of Byte;

  var
    GrDriver,
    GrMode,
    ErrCode,
    A,B,D,P  : Integer;
    F1       : BinFT;
    MSXVRAM  : array [0..$7FF] of Byte;

  begin
    if ParamCount=0 then begin
      WriteLn('MSX Graphos 3 "Alfabeto" File Viewer - Version 1.1.');
      WriteLn('(C) 1996 Unicorn High-Technology Products.');
      WriteLn('Programmed by "Cyberknight" Masao Kawata.');
      WriteLn;
      WriteLn('Usage: ',ParamStr(0),' <filename>.Alf');
      Halt(255);
      end;
    GrDriver:= CGA;
    GrMode:=CGAC1;
    InitGraph(GrDriver,GrMode,'');
    ErrCode:= GraphResult;
    if ErrCode<>GrOk then begin
      WriteLn('Couldn''t initialize graphic mode.');
      Halt(1);
      end;
    Assign(F1,ParamStr(1));
    Reset(F1);
    for A:=0 to 6 do
      Read(F1,MSXVRAM[A]);
    for A:=0 to $7FF do
      Read(F1,MSXVRAM[A]);
    Close(F1);
    SetColor(White);
    Rectangle(14,62,304,136);
    for A:=0 to $FF do
      for D:=0 to 7 do begin
        P:=MSXVRAM[A*8+D];
        for B:=0 to 7 do
          if (P and($80 shr B))<>0 then
            PutPixel((A mod 32)*8+B+(A mod 32)+16,(A div 32)*8+D+(A div 32)+64,15)
          else
            PutPixel((A mod 32)*8+B+(A mod 32)+16,(A div 32)*8+D+(A div 32)+64,0);
        end;
    while not KeyPressed do;
    CloseGraph;
  end.
