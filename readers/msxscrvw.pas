program G3ScrViewer;

  uses CRT,Graph;

  const
    GRPCGP = $0000;
    GRPCOL = $1800;

  type
    BinFT = file of byte;

  var
    GrDriver,
    GrMode,
    ErrCode,
    A,B,C,D,
    P,Q,R,S,T,
    E        : integer;
    F1       : BinFT;
    Buffer   : array [0..$3FFF] of byte;

  begin
    if ParamCount=0 then begin
      WriteLn('MSX Graphos 3 Display File Viewer - Version 1.2.');
      WriteLn('(C) 1996 Unicorn High-Technology Products.');
      WriteLn('Programmed by "Cyberknight" Masao Kawata.');
      WriteLn;
      WriteLn('Usage: ',ParamStr(0),' <filename>.Scr');
      Halt(255);
      end;
    GrDriver:= VGA;
    GrMode:=VGAHi;
    InitGraph(GrDriver,GrMode,'');
    ErrCode:= GraphResult;
    if ErrCode<>GrOk then begin
      WriteLn('Couldn''t initialize graphic mode.');
      Halt(1);
      end;
    SetRGBPalette( 0, 0, 0, 0);{ Incolor (border color) }
    SetRGBPalette( 1, 0, 0, 0);{ Black }
    SetRGBPalette( 2, 0,63, 0);{ Green }
    SetRGBPalette( 3,16,63,16);{ Light Green }
    SetRGBPalette( 4, 0, 0,50);{ Dark Blue }
    SetRGBPalette( 5,16,16,63);{ Light Blue }
    SetRGBPalette(20,50, 0, 0);{ Dark Red }
    SetRGBPalette( 7, 0,63,63);{ Cyan }
    SetRGBPalette(56,63, 0, 0);{ Red }
    SetRGBPalette(57,63,16,16);{ Light Red }
    SetRGBPalette(58,50,50, 0);{ Gold }
    SetRGBPalette(59,63,63, 0);{ Yellow }
    SetRGBPalette(60, 0,32, 0);{ Dark Green }
    SetRGBPalette(61,63, 0,63);{ Magenta }
    SetRGBPalette(62,50,50,50);{ Gray }
    SetRGBPalette(63,63,63,63);{ White }
    Assign(F1,ParamStr(1));
    Reset(F1);
    for A:=0 to 127 do
      Read(F1,Buffer[A]);
    for A:=0 to $17FF do
      Buffer[GRPCOL+A]:=$F0;
    A:=0;
    while (A<$3000)and(not EoF(F1)) do begin
      Read(F1,Buffer[A]);
      A:=A+1;
      end;{while}
    Close(F1);
    SetColor(White);
    Rectangle(190,142,449,337);
    for T:=0 to 2 do
      for A:=0 to $FF do begin
        B:=A*8+T*$800;
        for D:=0 to 7 do begin
          P:=Buffer[GRPCGP+B+D];
          C:=Buffer[GRPCOL+B+D];
          for E:=0 to 7 do
            if (P and($80 shr E))<>0 then
              PutPixel((A mod 32)*8+E+192,(A div 32)*8+T*64+D+144,C div 16)
            else
              PutPixel((A mod 32)*8+E+192,(A div 32)*8+T*64+D+144,C mod 16);
          end;{for E}
        end;{for A}
    while not KeyPressed do;
    CloseGraph;
  end.
