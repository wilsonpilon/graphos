program G3LayoutViewer;

  uses CRT,Graph;

  type
    BinFT = file of byte;

  var
    GrDriver,
    GrMode,
    ErrCode,
    A,B,C,D,
    P,T      : Integer;
    F1       : BinFT;
    Buffer  : array [0..$17FF] of Byte;
    E,F      : Byte;

  begin
    if ParamCount=0 then begin
      WriteLn('MSX Graphos 3 Layout File Viewer - Version 1.1.');
      WriteLn('(C) 1996 Unicorn High-Technology Products.');
      WriteLn('Programmed by "Cyberknight" Masao Kawata.');
      WriteLn;
      WriteLn('Usage: ',ParamStr(0),' <filename>.Lay');
      Halt(255);
      end;
    GrDriver:=CGA;
    GrMode:=CGAC1;
    InitGraph(GrDriver,GrMode,'');
    ErrCode:=GraphResult;
    if ErrCode<>GrOk then begin
      WriteLn('Couldn''t initialize graphic mode.');
      Halt(1);
      end;
    Assign(F1,ParamStr(1));
    Reset(F1);
    for B:=0 to 2 do
      Read(F1,E);
    Read(F1,E);
    Read(F1,F);
    A:=F*256+E+1-$9200;
    for B:=0 to 1 do
      Read(F1,E);
    B:=0;
    while A>0 do begin
      Read(F1,E);
      A:=A-1;
      if E>=$99 then
        E:=E-$99
      else
        E:=E+$67;
      if (E=0)or(E=$FF) then begin
        Read(F1,F);
        for C:=0 to F-1 do
          Buffer[B+C]:=E;
        B:=B+F;
        end
      else begin
        Buffer[B]:=E;
        B:=B+1;
        end;{else}
      if B>=$1800 then
        A:=0;
      end;{while}
    Close(F1);
    SetColor(White);
    Rectangle(30,2,289,197);
    for T:=0 to 2 do
      for A:=0 to $FF do begin
        B:=A*8+T*$800;
        for D:=0 to 7 do begin
          P:=Buffer[B+D];
          for E:=0 to 7 do
            if (P and($80 shr E))<>0 then
              PutPixel((A mod 32)*8+E+32,(A div 32)*8+T*64+D+4,15)
            else
              PutPixel((A mod 32)*8+E+32,(A div 32)*8+T*64+D+4,0);
          end;{for D}
        end;{for A}
    while not KeyPressed do;
    CloseGraph;
  end.
