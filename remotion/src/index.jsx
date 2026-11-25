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
const Root=()=> <Composition id="SyntheticMV" component={MV} durationInFrames={450} fps={30} width={1920} height={1080}/>;
registerRoot(Root);
