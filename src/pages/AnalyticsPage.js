import React from 'react';

const AnalyticsPage = ({ analytics = {} }) => {
  const chartData = [65, 70, 80, 75, 85, 90, 95];
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  
  return (
    <div>
      <h2>Analytics & Reports</h2>
      
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginTop: '2rem'}}>
        <div style={{background: 'white', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center'}}>
          <div style={{fontSize: '2rem', fontWeight: 'bold', color: '#667eea'}}>98.5%</div>
          <div style={{color: '#666', marginTop: '0.5rem'}}>Route Completion</div>
        </div>
        <div style={{background: 'white', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center'}}>
          <div style={{fontSize: '2rem', fontWeight: 'bold', color: '#667eea'}}>4.8</div>
          <div style={{color: '#666', marginTop: '0.5rem'}}>Customer Rating</div>
        </div>
        <div style={{background: 'white', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center'}}>
          <div style={{fontSize: '2rem', fontWeight: 'bold', color: '#667eea'}}>15%</div>
          <div style={{color: '#666', marginTop: '0.5rem'}}>Cost Reduction</div>
        </div>
        <div style={{background: 'white', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)', textAlign: 'center'}}>
          <div style={{fontSize: '2rem', fontWeight: 'bold', color: '#667eea'}}>28min</div>
          <div style={{color: '#666', marginTop: '0.5rem'}}>Avg Delivery</div>
        </div>
      </div>
      
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '2rem'}}>
        <div style={{background: 'white', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)'}}>
          <h3>📈 Weekly Performance</h3>
          <div style={{height: '300px', display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', padding: '1rem', background: '#f8f9fa', borderRadius: '0.5rem', marginTop: '1rem'}}>
            {chartData.map((height, i) => (
              <div key={i} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1}}>
                <div style={{width: '30px', height: `${height}%`, background: 'linear-gradient(135deg, #667eea, #764ba2)', borderRadius: '0.25rem 0.25rem 0 0', marginBottom: '0.5rem'}}></div>
                <span style={{fontSize: '0.75rem', color: '#666'}}>{days[i]}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div style={{background: 'white', padding: '1.5rem', borderRadius: '1rem', boxShadow: '0 4px 20px rgba(0,0,0,0.08)'}}>
          <h3>💰 Monthly Costs</h3>
          <div style={{marginTop: '1rem'}}>
            <div style={{marginBottom: '1rem'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem'}}>
                <span>Fuel</span>
                <span style={{fontWeight: 'bold'}}>$3,450</span>
              </div>
              <div style={{height: '8px', background: '#e0e0e0', borderRadius: '4px', overflow: 'hidden'}}>
                <div style={{height: '100%', width: '40%', background: '#667eea'}}></div>
              </div>
            </div>
            <div style={{marginBottom: '1rem'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem'}}>
                <span>Maintenance</span>
                <span style={{fontWeight: 'bold'}}>$1,200</span>
              </div>
              <div style={{height: '8px', background: '#e0e0e0', borderRadius: '4px', overflow: 'hidden'}}>
                <div style={{height: '100%', width: '15%', background: '#764ba2'}}></div>
              </div>
            </div>
            <div style={{marginBottom: '1rem'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem'}}>
                <span>Labor</span>
                <span style={{fontWeight: 'bold'}}>$8,500</span>
              </div>
              <div style={{height: '8px', background: '#e0e0e0', borderRadius: '4px', overflow: 'hidden'}}>
                <div style={{height: '100%', width: '65%', background: '#9575cd'}}></div>
              </div>
            </div>
            <div style={{paddingTop: '1rem', borderTop: '2px solid #e0e0e0', display: 'flex', justifyContent: 'space-between'}}>
              <span style={{fontWeight: 'bold'}}>Total</span>
              <span style={{fontWeight: 'bold', fontSize: '1.25rem', color: '#667eea'}}>$13,150</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
