"""
Converts sgy files (SEG-Y format) to dat files (3D arrays of floats)
Removes all SEG-Y headers and, if necessary, converts IBM floats to 
IEEE floats. The byte order for floats in dat files is BIG_ENDIAN. 

Author: Dave Hale, Colorado School of Mines
Version: 2010.11.05
"""
from imports import *

nhead=3200 # number of bytes in EBCDIC header
nbhed=400 # number of bytes in binary header
nthed=240 # number of bytes in trace header
bo=ByteOrder.BIG_ENDIAN # SEG-Y standard
global n1,n2,n3

#############################################################################
def main(args):
  goMbs()
  #goNorne()
  #goSino()
  #goParihaka()
  #goF3d()

def goMbs():
  """
  Subsets of PstmSmall:
  n1,nt = 501, dt = 0.0020, ft = 0.3 (s)
  n2,ny = 422, dy = 0.016764, fy = 0.0 (km) (dy = 55 ft), iline=1001:1422
  n3,nx = 448, dx = 0.016764, fx = 0.0 (km) (dx = 55 ft), xline= 601:1048
  Subsets of PstmLarge:
  n1,nt = 501, dt = 0.0020, ft = 0.3 (s)
  n2,ny = 422, dy = 0.016764, fy = 0.0 (km) (dy = 55 ft), iline=1001:1422
  n3,nx = 448, dx = 0.016764, fx = 0.0 (km) (dx = 55 ft), xline= 601:1048
  """
  global n1,n2,n3
  #n1,n2,n3 = 1500,422,448 # PstmSmall
  n1,n2,n3 = 1400,422,448 # PstmLarge raw
  fmt = 1 # IBM floats
  #nbytes = 961880880 # PstmSmall/Marathon20070209
  #nbytes = 959341200 # PstmSmall/Marathon20070228
  #nbytes = 4582266720 # PstmLarge fs
  nbytes = 4647376320 # PstmLarge raw
  ntrace = (nbytes-nhead-nbhed)/(240+4*n1)
  #sgydir = "/data/seis/mbs/PstmSmall/Marathon20070228/"
  #sgydir = "/data/seis/mbs/PstmSmall/Marathon20070228/"
  sgydir = "/data/seis/mbs/PstmLarge/"
  datdir = "/data/seis/mbs/dat/"
  #sgyfile = sgydir+"pstm_fraw.sgy"
  sgyfile = sgydir+"pstm_raw_cut.sgy"
  datfile = datdir+"pstm_raw_cut.dat"
  #readFormat(sgyfile) # format is 1, IBM floats
  #dumpTraceHeaders(sgyfile,fmt,n1,1000)
  #makeMap(sgyfile,None,nbytes,fmt,n1)
  #testFormat(n1,100,100,sgyfile) # yes, looks like IBM format
  convertMbs(n1,ntrace,sgyfile,datfile)
  #n1,n2,n3 = 501,422,448 # PstmSmall
  n1,n2,n3 = 501,1190,1114 # PstmLarge
  displayMbs(datfile,clip=5000.0)

def displayMbs(datfile,clip=0.0):
  x = readImage(datfile,n1,n2,n3)
  print "x min =",min(x)," max =",max(x)
  frame = SimpleFrame(AxesOrientation.XRIGHT_YIN_ZDOWN)
  s1,s2,s3 = Sampling(n1),Sampling(n2),Sampling(n3)
  ipg = frame.addImagePanels(s1,s2,s3,x)
  if clip>0.0:
    ipg.setClips(-clip,clip)

def convertMbs(n1,ntrace,sgyfile,datfile):
  #i1min,i1max =    0,1499 # PstmSmall
  #i2min,i2max = 1001,1422
  #i3min,i3max =  601,1048
  #i1min,i1max =  150, 650 # PstmSmall
  #i2min,i2max = 1001,1422
  #i3min,i3max =  601,1048
  i1min,i1max = 150, 650 # PstmLarge raw
  i2min,i2max = 234,1422
  i3min,i3max = 353,1468
  m1 = 1+i1max-i1min
  m2 = 1+i2max-i2min
  m3 = 1+i3max-i3min
  ais = ArrayInputStream(sgyfile,bo)
  ais.skipBytes(nhead)
  ais.skipBytes(nbhed)
  h = zeroint(nthed/4)
  x = zeroint(n1)
  y = zeroint(m1)
  z = zerofloat(m1,m2,m3)
  nread = 0
  nprev = 0
  for itrace in range(ntrace):
    nread += 1
    nperc = int(100.0*nread/ntrace)
    if nperc!=nprev and nperc%10==0:
      print "percent:",nperc
      nprev = nperc
    ais.readInts(h)
    i2,i3 = h[47],h[48]
    #print "nread =",nread," i2 =",i2," i3 =",i3
    #print "nread =",nread," i3min =",i3min," i3 =",i3," i3max =",i3max
    if i2min<=i2 and i2<=i2max and i3min<=i3 and i3<=i3max:
      #if i2==i2min:
      #  print "nread =",nread," i3min =",i3min," i3 =",i3," i3max =",i3max
      ais.readInts(x) # read trace samples
      copy(m1,i1min,x,0,y) # keep only m1 samples
      IbmIeee.ibmToFloat(y,z[i3-i3min][i2-i2min]) # ibm to ieee
    else:
      ais.skipBytes(4*n1)
  aos = ArrayOutputStream(datfile)
  aos.writeFloats(z) # write 3D image
  ais.close()
  aos.close()

""" 
Full Norne corner coordinates
line	trace	X	Y
970	2300	461652	7329340.16
970	1300	453320	7320021.12
1290	1300	456302	7317355
1290	2300	464634	7326674
Knut 16/7-09
"""
def goNorne():
  """
  E-Segment
  n1,nt = 1001, dt = 0.0040, ft = 0.0 (s)
  n2,ny =  401, dy = 0.0125, fy = 0.0 (km)
  n3,nx =  101, dx = 0.0125, fx = 0.0 (km)
  Full
  n1,nt = 1001, dt = 0.0040, ft = 0.0 (s)
  n2,ny = 1001, dy = 0.0125, fy = 0.0 (km)
  n3,nx =  321, dx = 0.0125, fx = 0.0 (km)
  """
  global n1,n2,n3
  #n1,n2,n3 = 1001,401,101
  #datdir = "/data/seis/norne/eseg/"
  #sgyfile = datdir+"ESEG-NORNE-2004-FULL.sgy"
  #datfile = datdir+"eseg2004full.dat"
  n1,n2,n3 = 1001,1001,321
  datdir = "/data/seis/norne/all/"
  sgyfile = datdir+"norne4d_2006-full.sgy"
  datfile = datdir+"all2006full.dat"
  #readFormat(sgyfile) # format is 1, IBM floats
  #dumpTraceHeaders(sgyfile,1,1001)
  #testFormat(n1,n2,n3,sgyfile) # yes, looks like IBM format
  #convert(n1,n2,n3,sgyfile,datfile)
  displayNorne(datfile)

def displayNorne(datfile):
  global n1
  clip = 1000.0
  x = readImage(datfile,n1,n2,n3)
  #n1,j1 = 601,320
  #x = copy(n1,n2,n3,j1,0,0,x)
  #print "x min =",min(x)," max =",max(x)
  s1,s2,s3 = Sampling(n1),Sampling(n2),Sampling(n3)
  frame = SimpleFrame(AxesOrientation.XRIGHT_YIN_ZDOWN)
  ipg = frame.addImagePanels(s1,s2,s3,x)
  ipg.setClips(-clip,clip)

def goSino():
  global bo
  bo = ByteOrder.LITTLE_ENDIAN # non-standard byte-order
  """
  nt = 2001, dt = 0.004 s, (ft = 0.000 s?)
  """
  n1,n2,n3 = 2001,721,1
  datdir = "/data/seis/sinopec/"
  for component in ["x","z"]:
    sgyfile = datdir+"260_"+component+"_201-921_stack.segy"
    datfile = datdir+component+"260.dat"
    #readFormat(sgyfile)
    #testFormat(n1,n2,n3,sgyfile)
    #convert(n1,n2,n3,sgyfile,datfile)
    f = readImage(datfile,n1,n2)
    if component=="z":
      stretch(1.6,f)
      #mul(pow(rampfloat(0.0,1.0,0.0,n1,n2),2.0),f,f)
    else:
      #mul(pow(rampfloat(0.0,1.0,0.0,n1,n2),0.0),f,f)
      pass
    lowpass(0.10,f)
    gain(50,f)
    plot2(f,title=component+" component")

def lowpass(f3db,f):
  bf = ButterworthFilter(f3db,6,ButterworthFilter.Type.LOW_PASS)
  bf.apply1ForwardReverse(f,f)

def gain(hw,f):
  g = mul(f,f)
  RecursiveExponentialFilter(hw).apply1(g,g)
  div(f,sqrt(g),f)

def stretch(c,f):
  n1,n2 = len(f[0]),len(f)
  t = rampfloat(0.0,1.0/c,n1)
  si = SincInterpolator()
  si.setUniformSampling(n1,1.0,0.0)
  g = zerofloat(n1)
  for i2 in range(n2):
    si.setUniformSamples(f[i2])
    si.interpolate(n1,1.0/c,0.0,g)
    copy(g,f[i2])

def plot2(x,title=None):
  sp = SimplePlot(SimplePlot.Origin.UPPER_LEFT)
  sp.setSize(350,1100)
  if title:
    sp.setTitle(title)
  pv = sp.addPixels(x)
  pv.setPercentiles(2,98)
  
def goF3d():
  """
  TIME: 462 samples (1.848 sec, interval 4 ms)
  nbytes = 699,003,060
  ntrace = (nbytes-nhead-nbhed)/(240+2*n1)
  """
  fmt = 3 # 2-byte shorts in [-32767,32767]
  global n1,n2,n3
  n1,n2,n3 = 462,951,591
  nbytes = 699003060
  datdir = "/data/seis/f3d/"
  sgyfile = datdir+"f3draw.sgy"
  mapfile = datdir+"f3dmap.dat"
  datfile = datdir+"f3draw.dat"
  displayF3d(datfile)
  #displayF3dTrace(datfile)
  #makeSubsetsF3d(datdir)
  #displaySubsetF3d(datfile,0,500,500,751,501,501)
  #bigSubsetF3d(n1,sgyfile,datfile)
  #readFormat(sgyfile)
  #makeMap(sgyfile,mapfile,nbytes,fmt,n1)
  #dumpTraceHeaders(sgyfile,fmt,n1)
  #convert3(n1,n2,n3,sgyfile,datfile)

def displayF3d(datfile):
  x = readImage(datfile,n1,n2,n3)
  xmax = 30767.0
  display3d(sub(x,clip(-xmax,xmax,x)),1.0)
  #mul(0.001,x,x)
  #display3d(x,10.0)
  #display3d(slog(x),3.0)


def displayF3dTrace(datfile):
  x = readImage(datfile,n1,n2,n3)
  mul(0.001,x,x)
  x = x[170][252]
  SimplePlot.asPoints(x)
  SimplePlot.asPoints(spow(0.5,x))
  SimplePlot.asPoints(slog(x))

def spow(p,f):
  return mul(sgn(f),pow(abs(f),p))

def slog(f):
  return mul(sgn(f),log(add(1.0,abs(f))))

def sexp(f):
  return mul(sgn(f),sub(exp(abs(f)),1.0))

def goParihaka():
  """
  INLINES  : 1665 - 5599 (INC 1)   CROSSLINES : 2050 - 14026 (INC 2)
  TIME: 1501 samples  (6 sec, interval 4ms)
  nbytes = 69,479,807,644
  ntrace = (nbytes-nhead-nbhed)/(240+4*n1)
  """
  fmt = 1
  n1 = 1501
  nbytes = 69479807644
  datdir = "/data/seis/nz/par/"
  sgyfile = datdir+"Parihaka3d_raw.sgy"
  mapfile = datdir+"map.dat"
  datfile = datdir+"par11.dat"
  #displayParihaka(datfile)
  #makeSubsetsParihaka(datdir)
  #displaySubsetParihaka(datfile,0,500,500,751,501,501)
  #bigSubsetParihaka(n1,sgyfile,datfile)
  readFormat(sgyfile)
  #makeMap(sgyfile,mapfile,nbytes,n1)
  #dumpTraceHeaders(sgyfile,fmt,n1)
  #testFormat(n1,n2,n3,sgyfile)
  #convert(n1,n2,n3,sgyfile,datfile)

def displayParihaka(datfile):
  n1,n2,n3 = 751,1001,1001
  x = readImage(datfile,n1,n2,n3)
  display3d(x,1.0e5)

def makeSubsetsParihaka(datdir):
  m1,m2,m3 = 751,1001,1001
  x = readParihaka(datdir+"parBig.dat",0,0,0,m1,m2,m3)
  writeImage(datdir+"par00.dat",x)
  x = None
  x = readParihaka(datdir+"parBig.dat",0,1000,0,m1,m2,m3)
  writeImage(datdir+"par01.dat",x)
  x = None
  x = readParihaka(datdir+"parBig.dat",0,0,1000,m1,m2,m3)
  writeImage(datdir+"par10.dat",x)
  x = None
  x = readParihaka(datdir+"parBig.dat",0,1000,1000,m1,m2,m3)
  writeImage(datdir+"par11.dat",x)
  display3d(x,1.0e5)

def displaySubsetParihaka(datfile,j1,j2,j3,m1,m2,m3):
  x = readSubsetParihaka(datfile,j1,j2,j3,m1,m2,m3)
  display3d(x,1.0e5)

def readImage(datfile,n1,n2,n3=1):
  if n3==1:
    x = zerofloat(n1,n2)
  else:
    x = zerofloat(n1,n2,n3)
  ais = ArrayInputStream(datfile)
  ais.readFloats(x)
  ais.close()
  return x

def writeImage(datfile,x):
  aos = ArrayOutputStream(datfile)
  aos.writeFloats(x)
  aos.close()

def readParihaka(datfile,j1,j2,j3,m1,m2,m3):
  n1,n2,n3 = 1501,2001,2001
  m1 = min(m1,n1)
  m2 = min(m2,n2)
  m3 = min(m3,n3)
  j1 = min(j1,n1-m1)
  j2 = min(j2,n2-m2)
  j3 = min(j3,n3-m3)
  x = zerofloat(m1,m2,m3)
  ais = ArrayInputStream(datfile)
  for i3 in range(j3):
    ais.skipBytes(4*n1*n2)
  ais.skipBytes(4*(j1+n1*j2))
  for i3 in range(m3):
    if i3%10==0: 
      print "i3 =",i3
    for i2 in range(m2):
      ais.readFloats(x[i3][i2])
      ais.skipBytes(4*(n1-m1))
    ais.skipBytes(4*n1*(n2-m2))
  return x

def bigSubsetParihaka(n1,sgyfile,datfile):
  """ big subset 1501x2001x2001 ~ 24 GB
  i1min,i1max =    0, 1500 # time samples
  i2min,i2max = 6500,10500 # increment by 2
  i3min,i3max = 2100, 4100 # increment by 1
  """
  """ A: small subset 501x501x501 ~ 500 MB
  i1min,i1max =    0, 500 # time samples
  i2min,i2max = 7500,8500 # increment by 2
  i3min,i3max = 2500,3000 # increment by 1
  """
  """ B: subset 751x1001x1001 ~ 500 MB
  i1min,i1max =    0, 750 # time samples
  i2min,i2max = 7000,9000 # increment by 2
  i3min,i3max = 3000,4000 # increment by 1
  """
  i1min,i1max =    0, 1500 # time samples
  i2min,i2max = 6500,10500 # increment by 2
  i3min,i3max = 2100, 4100 # increment by 1
  m1 = 1+i1max-i1min
  m2 = 1+(i2max-i2min)/2
  m3 = 1+i3max-i3min
  m23 = m2*m3
  ais = ArrayInputStream(sgyfile,bo)
  aos = ArrayOutputStream(datfile)
  ais.skipBytes(nhead)
  ais.skipBytes(nbhed)
  h = zeroint(nthed/4)
  x = zeroint(n1)
  y = zeroint(m1)
  z = zerofloat(m1)
  nread = 0
  i23 = 0
  while i23<m23:
    nread += 1
    ais.readInts(h)
    i3,i2 = h[49],h[50]
    if i2min<=i2 and i2<=i2max and i3min<=i3 and i3<=i3max:
      i23 += 1
      if i2==i2min:
        print "nread =",nread," i3min =",i3min," i3 =",i3," i3max =",i3max
      ais.readInts(x) # read trace samples
      copy(m1,x,y) # keep only m1 samples
      IbmIeee.ibmToFloat(y,z) # ibm to ieee
      aos.writeFloats(z) # write trace samples
    else:
      ais.skipBytes(4*n1)
  ais.close()
  aos.close()

def makeMap(sgyfile,mapfile,nbytes,fmt,n1):
  if fmt==3:
    bps = 2
  else:
    bps = 4
  ntrace = (nbytes-nhead-nbhed)/(240+bps*n1)
  af = ArrayFile(sgyfile,"r")
  af.skipBytes(nhead)
  af.skipBytes(nbhed)
  h = zeroint(nthed/4)
  #m2,m3 = 8000,16000 # Parihaka
  #m2,m3 = 800,1300 # F3D
  #m2,m3 = 800,1300 # Norne
  m2,m3 = 1422,1043 # Mbs
  m = zerofloat(m2,m3)
  i2min =  Integer.MAX_VALUE
  i2max = -Integer.MAX_VALUE
  i3min =  Integer.MAX_VALUE
  i3max = -Integer.MAX_VALUE
  for i in range(ntrace):
    #if i%100==0:
    #  print "i =",i
    #  print "i2:  min =",i2min," max =",i2max
    #  print "i3:  min =",i3min," max =",i3max
    af.readInts(h)
    #i2,i3 = h[49],h[50] # Parihaka
    i2,i3 = h[47],h[48] # F3D, Norne, Mbs
    if 0<=i2 and i2<m2 and 0<=i3 and i3<m3:
      m[i3][i2] = 1.0
    #print "i =",i," i2 =",i2," i3 =",i3
    if i2<i2min: i2min = i2
    if i2>i2max: i2max = i2
    if i3<i3min: i3min = i3
    if i3>i3max: i3max = i3
    af.skipBytes(bps*n1)
    af.seek(af.filePointer+100*(nthed+bps*n1))
  af.close()
  print "i2:  min =",i2min," max =",i2max
  print "i3:  min =",i3min," max =",i3max
  sp = SimplePlot()
  pv = sp.addPixels(m)
  pv.setInterpolation(PixelsView.Interpolation.NEAREST)
  if mapfile:
    aos = ArrayOutputStream(mapfile)
    aos.writeFloats(m)
    aos.close()


def dumpTraceHeaders(sgyfile,fmt,n1,ndump=5):
  af = ArrayFile(sgyfile,"r")
  af.skipBytes(nhead)
  af.skipBytes(nbhed)
  hi = zeroint(nthed/4)
  hs = zeroshort(nthed/2)
  for i in range(ndump):
    fp = af.getFilePointer()
    af.readInts(hi)
    af.seek(fp)
    af.readShorts(hs)
    print "ensemble number =",hi[5]
    print "trace in ensemble =",hi[6]
    print "coord scale factor =",hs[35]
    print "x,y coord =",hi[45],hi[46]
    print "iline,xline =",hi[47],hi[48]
    #print "iline,xline =",hi[49],hi[50]
    #dump(hi)
    #dump(hs)
    if fmt==3:
      af.skipBytes(2*n1)
    else:
      af.skipBytes(4*n1)
  af.close()

def goParihakaSubsets():
  #n1,n2,n3 = 751,1501,701
  n1,n2,n3 = 751,1501,601
  datdir = "/data/seis/nz/par/"
  sgyfile = datdir+"parihaka_subset3.sgy"
  datfile = datdir+"par3.dat"
  check(n1,n2,n3,sgyfile)
  #readFormat(sgyfile)
  #testFormat(n1,n2,n3,sgyfile)
  #convert(n1,n2,n3,sgyfile,datfile)
  #display3d(n1,n2,n3,datfile,2.0e4)

def checkSubset(n1,n2,n3,sgyfile):
  print "checking",(n2*n3),"traces"
  nh = nthed/2
  nx = n1
  h = zeroshort(nh)
  x = zeroint(nx)
  ais = ArrayInputStream(sgyfile,bo)
  ais.skipBytes(nhead+nbhed)
  for i3 in range(n3):
    for i2 in range(n2):
      ais.readShorts(h) # read trace header
      ais.readInts(x) # read trace samples
      ns = h[57] # number of samples in this trace
      if ns!=n1:
        print "*** i2 =",i2,"i3 =",i3,"ns =",ns
        print "*** trace header as shorts:"
        dump(h)
        return
    print "checked: i3 =",i3
  ais.close()

def convert(n1,n2,n3,sgyfile,datfile):
  print "converting",(n2*n3),"traces"
  ais = ArrayInputStream(sgyfile,bo)
  aos = ArrayOutputStream(datfile)
  ais.skipBytes(nhead+nbhed)
  x = zeroint(n1)
  y = zerofloat(n1)
  for i3 in range(n3):
    for i2 in range(n2):
      ais.skipBytes(nthed) # skip trace header
      ais.readInts(x) # read trace samples
      IbmIeee.ibmToFloat(x,y) # convert
      aos.writeFloats(y) # write trace samples
    print "converted: i3 =",i3," n2 =",n2
  ais.close()
  aos.close()

def convert3(n1,n2,n3,sgyfile,datfile):
  print "converting",(n2*n3),"traces"
  ais = ArrayInputStream(sgyfile,bo)
  aos = ArrayOutputStream(datfile)
  ais.skipBytes(nhead+nbhed)
  x = zeroshort(n1)
  y = zerofloat(n1)
  for i3 in range(n3):
    for i2 in range(n2):
      ais.skipBytes(nthed) # skip trace header
      ais.readShorts(x) # read trace samples
      IbmIeee.shortToFloat(x,y) # convert
      aos.writeFloats(y) # write trace samples
    print "converted: i3 =",i3
  ais.close()
  aos.close()

def display3d(x,clip=0):
  n1,n2,n3 = len(x[0][0]),len(x[0]),len(x)
  print "x min =",min(x)," max =",max(x)
  s1,s2,s3 = Sampling(n1),Sampling(n2),Sampling(n3)
  frame = SimpleFrame()
  ipg = frame.addImagePanels(s1,s2,s3,x)
  if clip>0.0:
    ipg.setClips(-clip,clip)
  frame.setVisible(True)

def displayFile3d(datfile,n1,n2,n3,clip=0):
  x = zerofloat(n1,n2,n3)
  ais = ArrayInputStream(datfile)
  ais.readFloats(x)
  ais.close()
  display3d(x,clip)

def readFormat(sgyfile):
  ais = ArrayInputStream(sgyfile,bo)
  ais.skipBytes(nhead)
# floating point format code should be in bytes 3225-6
# 1 for IBM floating point, 5 for IEEE floating point
  h = zeroshort(nbhed/2)
  ais.readShorts(h)
  ais.close()
  print "dump of binary header as shorts"
  dump(h)
  print "current sampling interval in usec =",h[8]
  print "original sampling interval in usec =",h[9]
  print "number of samples per trace =",h[10]
  print "original number of samples per trace =",h[11]
  format = h[12]
  if format==1:
    print "format = 1 = IBM floating point"
  elif format==3:
    print "format = 3 = 2-byte two's complement integer"
  elif format==5:
    print "format = 5 = IEEE floating point"
  else:
    print "format =",format,"is unknown!"

def testFormat(n1,n2,n3,sgyfile):
  xi = zeroint(n1)
  x1 = zerofloat(n1)
  x2 = zerofloat(n1)
  ais = ArrayInputStream(sgyfile,bo)
  ais.skipBytes(nhead+nbhed)
  ais.skipBytes(n3/2*n2*(nthed+4*n1))
  ais.skipBytes(n2/2*(nthed+4*n1))
  ais.skipBytes(nthed)
  ais.readInts(xi)
  ais.close()
  IbmIeee.ibmToFloat(xi,x1)
  IbmIeee.ieeeToFloat(xi,x2)
  sp = SimplePlot.asPoints(x1); sp.setTitle("Assuming IBM format")
  sp = SimplePlot.asPoints(x2); sp.setTitle("Assuming IEEE format")

#############################################################################
class RunMain(Runnable):
  def run(self):
    main(sys.argv)
SwingUtilities.invokeLater(RunMain()) 
