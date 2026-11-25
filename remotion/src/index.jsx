import React from 'react';
import {AbsoluteFill, Audio, Composition, interpolate, registerRoot, staticFile, useCurrentFrame} from 'remotion';

const colors=['#60a5fa','#c4b5fd','#5eead4'];
const labels=['INTRO / 01','VERSE / 02','CHORUS / 03'];
const lines=['A new signal','A quiet horizon','A brighter frame'];
const MV=()=>{
  const f=useCurrentFrame();
  const scene=Math.min(2,Math.floor(f/150));
  const local=f%150;
  const phase=f%15;
  const beat=Math.exp(-phase/4);
  const opacity=interpolate(local,[0,12,137,149],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
  return <AbsoluteFill style={{background:'#101b2d',fontFamily:'Arial, sans-serif',color:'#f0f5fb',overflow:'hidden'}}>
    <Audio src={staticFile('synthetic.wav')}/>
    <div style={{position:'absolute',width:620,height:620,borderRadius:'50%',left:650,top:225,background:'radial-gradient(circle, '+colors[scene]+' 0%, transparent 70%)',opacity:0.25+beat*0.18,transform:'scale('+(1+beat*.05)+')'}}/>
    {Array.from({length:24},(_,i)=><div key={i} style={{position:'absolute',left:460+i*42,bottom:178,width:19,height:45+90*(0.25+0.75*beat)*Math.abs(Math.sin(i*.7+f*.04)),borderRadius:10,background:colors[scene],opacity:.75}}/>)}
    <div style={{position:'absolute',top:86,left:96,fontSize:28,letterSpacing:5,color:colors[scene]}}>GACKY-LAB / SYNTHETIC MV</div>
    <div style={{position:'absolute',left:0,right:0,top:392,textAlign:'center',opacity,transform:'translateY('+((1-opacity)*20)+'px)'}}>
      <div style={{fontSize:26,letterSpacing:6,color:colors[scene]}}>{labels[scene]}</div>
      <div style={{fontSize:76,fontWeight:700,marginTop:25}}>{lines[scene]}</div>
    </div>
    <div style={{position:'absolute',left:96,bottom:75,fontSize:23,color:'#adbed1'}}>120 BPM / GENERATED TEST TONE / NO REAL SONG</div>
    <div style={{position:'absolute',left:96,bottom:45,height:5,width:1728*(f+1)/450,background:colors[scene]}}/>
  </AbsoluteFill>;
};
const LyricPreview=({cues=[],pulses=[],synthetic=false})=>{
  const f=useCurrentFrame();
  const cue=cues.find(c=>f>=c.startFrame&&f<c.endFrame);
  const recent=pulses.filter(p=>p<=f).at(-1);
  const energy=recent===undefined?0:Math.exp(-(f-recent)/5);
  const scene=Math.floor(f/150)%3;
  const color=colors[scene];
  const move=18*Math.sin(f/90);
  return <AbsoluteFill style={{background:'linear-gradient(135deg,#101b2d,#17344a)',color:'#f0f5fb',fontFamily:'Arial, sans-serif',overflow:'hidden'}}>
    <Audio src={staticFile('preview.wav')}/>
    <div style={{position:'absolute',left:460+move,top:100,width:1000,height:860,borderRadius:'50%',background:'radial-gradient(ellipse,'+color+',transparent 68%)',opacity:.13+energy*.13}}/>
    <div style={{position:'absolute',top:90,left:100,fontSize:26,letterSpacing:5,color}}>GACKY-LAB / {synthetic?'SYNTHETIC DEMO':'LOCAL LYRIC PREVIEW'}</div>
    <div style={{position:'absolute',left:150,right:150,top:370,height:330,display:'flex',alignItems:'center',justifyContent:'center',fontSize:cue&&cue.text.length>35?52:72,fontWeight:700,textAlign:'center',overflowWrap:'anywhere',lineHeight:1.35}}>{cue?.text||''}</div>
    <div style={{position:'absolute',left:100,bottom:86,color:'#adbed1',fontSize:24}}>PREVIEW / HUMAN REVIEW REQUIRED</div>
    <div style={{position:'absolute',left:100,bottom:48,height:5,width:1720*(f+1)/900,background:color}}/>
  </AbsoluteFill>;
};
const Root=()=> <><Composition id="SyntheticMV" component={MV} durationInFrames={450} fps={30} width={1920} height={1080}/><Composition id="LyricPreview" component={LyricPreview} durationInFrames={900} fps={30} width={1920} height={1080} defaultProps={{cues:[],pulses:[],synthetic:false}}/></>;
registerRoot(Root);
