program G3ShapeViewer;

  uses CRT,Graph;

  const
    GRPCGP = $0000;
    GRPCOL = $1800;
    GRPMsk = $3000;

  type
    BinFT = file of Byte;

  var
    GrDriver,
    GrMode,
    ErrCode,
    A,B,C,D,E: Integer;
    F1       : BinFT;
    K,T,S,H,W: Byte;
    N,P      : string;
    Buffer   : array [0..$47FF] of Byte;

  procedure ShowShape(W,H:Integer;M:Byte);

    var
      X,Y,P,T: Integer;

    begin
      for Y:=0 to H-1 do
        for X:=0 to W-1 do begin
          A:=X+Y*W;
          B:=A*8;
          A:=X+Y*32;
          T:=A div 256;
          A:=A mod 256;
          for D:=0 to 7 do begin
            P:=Buffer[GRPCGP+B+D+M*GRPMsk];
            C:=Buffer[GRPCOL+B+D];
            for E:=0 to 7 do
              if (P and($80 shr E))<>0 then
                PutPixel((A mod 32)*8+E+192,(A div 32)*8+T*64+D+144,C div 16)
              else
                PutPixel((A mod 32)*8+E+192,(A div 32)*8+T*64+D+144,C mod 16);
            end;{for D}
          end;{for X}
    end;{procedure Show Screen}

  begin
    if ParamCount=0 then begin
      WriteLn('MSX Graphos 3 Shape File Viewer - Version 1.0.');
      WriteLn('(C) 1996 Unicorn High-Technology Products.');
      WriteLn('Programmed by "Cyberknight" Masao Kawata.');
      WriteLn;
      WriteLn('Usage: ',ParamStr(0),' <filename>.Shp');
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
    SetColor(White);
    SetBkColor(Black);
    SetFillStyle(EmptyFill,White);
    Read(F1,K);
    repeat
      if K<>$FF then begin
        Read(F1,T);
        Read(F1,S);
        Read(F1,H);
        W:=S div 8;
        Str(K:3,N);
        N:='Shape: '+N+'  Type: ';
        Str(T:1,P);
        N:=N+P+'  Size: (';
        Str(W:2,P);
        N:=N+P+',';
        Str(H:2,P);
        N:=N+P+')';
        Bar(190,130,460,138);
        OutTextXY(190,130,N);
        Bar(190,142,449,337);
        Rectangle(190,142,193+S,145+H*8);
        case T of
          1:begin
            for A:=0 to (S*H)-1 do begin
              Read(F1,Buffer[A+GRPCGP]);
              Buffer[A+GRPCOL]:=$F0;
              end;{for}
            ShowShape(W,H,0);
            end;{case 1}
          2:begin
            for A:=0 to (S*H)-1 do begin
              Read(F1,Buffer[A+GRPCGP]);
              end;{for}
            for A:=0 to (S*H)-1 do begin
              Read(F1,Buffer[A+GRPCOL]);
              end;{for}
            ShowShape(W,H,0);
            end;{case 2}
          3:begin
            for A:=0 to (S*H)-1 do begin
              Read(F1,Buffer[A+GRPMsk]);
              Buffer[A+GRPCOL]:=$F0;
              end;{for}
            for A:=0 to (S*H)-1 do begin
              Read(F1,Buffer[A+GRPCGP]);
              end;{for}
            ShowShape(W,H,0);
            ReadKey;
            ShowShape(W,H,1);
            end;{case 3}
          4:begin
            for A:=0 to (S*H)-1 do begin
              Read(F1,Buffer[A+GRPMsk]);
              Buffer[A+GRPCOL]:=$F0;
              end;{for}
            for A:=0 to (S*H)-1 do begin
              Read(F1,Buffer[A+GRPCGP]);
              end;{for}
            for A:=0 to (S*H)-1 do begin
              Read(F1,Buffer[A+GRPCOL]);
              end;{for}
            ShowShape(W,H,0);
            ReadKey;
            ShowShape(W,H,1);
            end;{case 4}
          end;{case}
        end;{if}
      Read(F1,K);
      until (ReadKey=#27)or(K=$FF);
    Close(F1);
    CloseGraph;
  end.
