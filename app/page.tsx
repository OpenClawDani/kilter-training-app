'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #000 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      overflow: 'hidden',
      padding: '20px',
      position: 'relative'
    }}>
      {/* Top nav */}
      <div style={{position: 'absolute', top: 0, left: 0, right: 0, display: 'flex', justifyContent: 'flex-end', padding: '16px 24px', zIndex: 20}}>
        <Link href="/login" style={{color: '#cbd5e1', fontSize: '14px', fontWeight: 600, textDecoration: 'none', padding: '8px 20px', border: '1px solid rgba(255, 107, 53, 0.4)', borderRadius: '8px', transition: 'all 0.3s ease'}}>
          Login
        </Link>
      </div>
      {/* Background animated elements */}
      <div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
        <div style={{position: 'absolute', top: 0, right: 0, width: '400px', height: '400px', background: 'rgba(255, 107, 53, 0.1)', borderRadius: '50%', filter: 'blur(80px)'}}></div>
        <div style={{position: 'absolute', bottom: 0, left: 0, width: '400px', height: '400px', background: 'rgba(255, 107, 53, 0.15)', borderRadius: '50%', filter: 'blur(80px)'}}></div>
      </div>

      <div style={{position: 'relative', zIndex: 10, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '32px', maxWidth: '800px', width: '100%'}}>
        {/* Kilterboard Image */}
        <div style={{position: 'relative', width: '100%', maxWidth: '400px'}}>
          <div style={{aspectRatio: '1', borderRadius: '16px', overflow: 'hidden', boxShadow: '0 25px 50px rgba(0,0,0,0.8)', border: '2px solid rgba(255, 107, 53, 0.3)'}}>
            <img
              src="https://images.pexels.com/photos/2398220/pexels-photo-2398220.jpeg?w=600&h=600&fit=crop"
              alt="Kilterboard climbing wall"
              style={{width: '100%', height: '100%', objectFit: 'cover', display: 'block'}}
              loading="eager"
            />
          </div>
          {/* Glow effect */}
          <div style={{position: 'absolute', inset: 0, borderRadius: '16px', background: 'linear-gradient(to top, rgba(255, 107, 53, 0.3), transparent)', pointerEvents: 'none'}}></div>
          <div style={{position: 'absolute', inset: '-4px', borderRadius: '16px', background: 'linear-gradient(135deg, #FF6B35, #FF8C42)', opacity: 0.2, filter: 'blur(20px)', zIndex: -1}}></div>
        </div>

        {/* KILTER UP Heading - VIVID ORANGE */}
        <div style={{textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '16px'}}>
          <h1 style={{fontSize: 'clamp(48px, 10vw, 96px)', fontWeight: 900, color: '#FF6B35', textShadow: '0 0 40px rgba(255, 107, 53, 0.8)', letterSpacing: '-2px', margin: 0}}>
            KILTER UP
          </h1>
          <p style={{fontSize: '18px', color: '#cbd5e1', maxWidth: '500px', fontWeight: 500, margin: 0}}>
            AI-Powered Circuit Generation &amp; Training Planning for Kilterboard
          </p>
        </div>

        {/* CTA Button - PREMIUM */}
        <Link href="/login" style={{marginTop: '32px', padding: '16px 32px', background: 'linear-gradient(135deg, #FF6B35, #FF8C42)', color: 'white', fontWeight: 'bold', fontSize: '16px', border: 'none', borderRadius: '8px', boxShadow: '0 20px 40px rgba(255, 107, 53, 0.4)', cursor: 'pointer', transition: 'all 0.3s ease', textDecoration: 'none', display: 'inline-block'}}
          onMouseOver={(e) => {e.currentTarget.style.transform = 'scale(1.05)'; e.currentTarget.style.boxShadow = '0 30px 60px rgba(255, 107, 53, 0.6)'}}
          onMouseOut={(e) => {e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.boxShadow = '0 20px 40px rgba(255, 107, 53, 0.4)'}}
        >
          Inizia 🧗‍♂️
        </Link>

        {/* Feature cards */}
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px', marginTop: '48px', paddingTop: '32px', borderTop: '1px solid rgba(255, 107, 53, 0.2)', width: '100%'}}>
          <div style={{textAlign: 'center', padding: '16px', borderRadius: '8px', background: 'rgba(255, 107, 53, 0.05)', border: '1px solid rgba(255, 107, 53, 0.2)', transition: 'all 0.3s ease', cursor: 'pointer'}}
            onMouseOver={(e) => {e.currentTarget.style.borderColor = 'rgba(255, 107, 53, 0.5)'; e.currentTarget.style.background = 'rgba(255, 107, 53, 0.1)'}}
            onMouseOut={(e) => {e.currentTarget.style.borderColor = 'rgba(255, 107, 53, 0.2)'; e.currentTarget.style.background = 'rgba(255, 107, 53, 0.05)'}}
          >
            <div style={{fontSize: '32px', marginBottom: '8px'}}>🎬</div>
            <p style={{fontSize: '14px', fontWeight: 600, color: '#cbd5e1', margin: 0}}>Video Analysis</p>
          </div>
          <div style={{textAlign: 'center', padding: '16px', borderRadius: '8px', background: 'rgba(255, 107, 53, 0.05)', border: '1px solid rgba(255, 107, 53, 0.2)', transition: 'all 0.3s ease', cursor: 'pointer'}}
            onMouseOver={(e) => {e.currentTarget.style.borderColor = 'rgba(255, 107, 53, 0.5)'; e.currentTarget.style.background = 'rgba(255, 107, 53, 0.1)'}}
            onMouseOut={(e) => {e.currentTarget.style.borderColor = 'rgba(255, 107, 53, 0.2)'; e.currentTarget.style.background = 'rgba(255, 107, 53, 0.05)'}}
          >
            <div style={{fontSize: '32px', marginBottom: '8px'}}>🤖</div>
            <p style={{fontSize: '14px', fontWeight: 600, color: '#cbd5e1', margin: 0}}>AI Circuits</p>
          </div>
          <div style={{textAlign: 'center', padding: '16px', borderRadius: '8px', background: 'rgba(255, 107, 53, 0.05)', border: '1px solid rgba(255, 107, 53, 0.2)', transition: 'all 0.3s ease', cursor: 'pointer'}}
            onMouseOver={(e) => {e.currentTarget.style.borderColor = 'rgba(255, 107, 53, 0.5)'; e.currentTarget.style.background = 'rgba(255, 107, 53, 0.1)'}}
            onMouseOut={(e) => {e.currentTarget.style.borderColor = 'rgba(255, 107, 53, 0.2)'; e.currentTarget.style.background = 'rgba(255, 107, 53, 0.05)'}}
          >
            <div style={{fontSize: '32px', marginBottom: '8px'}}>📊</div>
            <p style={{fontSize: '14px', fontWeight: 600, color: '#cbd5e1', margin: 0}}>Training Plans</p>
          </div>
        </div>
      </div>
    </div>
  );
}
