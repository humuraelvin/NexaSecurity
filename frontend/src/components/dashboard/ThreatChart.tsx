"use client"
import { useEffect, useRef } from 'react';
import { format } from 'date-fns';
import { Chart, registerables } from 'chart.js';

// Register Chart.js components
Chart.register(...registerables);

interface ThreatChartProps {
  data: any[];
  isLoading?: boolean;
}

export default function ThreatChart({ data, isLoading }: ThreatChartProps) {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  useEffect(() => {
    if (isLoading || !data || !chartRef.current) return;

    // Destroy previous chart instance if it exists
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    if (!ctx) return;

    // Process data for the chart
    const labels = data.map(item => format(new Date(item.timestamp), 'HH:mm'));
    const values = data.map(item => item.threats);

    // Create new chart
    chartInstance.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Threats',
            data: values,
            borderColor: '#22d3ee',
            backgroundColor: 'rgba(34, 211, 238, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: true,
            pointRadius: 0,
            pointHoverRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(17, 24, 39, 0.8)',
            titleColor: '#ffffff',
            bodyColor: '#d1d5db',
            borderColor: '#374151',
            borderWidth: 1,
          },
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(75, 85, 99, 0.2)',
            },
            ticks: {
              color: '#9ca3af',
              maxRotation: 0,
              autoSkip: true,
              maxTicksLimit: 12,
            },
          },
          y: {
            grid: {
              color: 'rgba(75, 85, 99, 0.2)',
            },
            ticks: {
              color: '#9ca3af',
            },
            beginAtZero: true,
          },
        },
        interaction: {
          mode: 'nearest',
          intersect: false,
        },
      },
    });

    // Cleanup function
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data, isLoading]);

  if (isLoading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-solid border-cyan-400 border-r-transparent"></div>
      </div>
    );
  }

  return (
    <div className="h-64">
      <canvas ref={chartRef} />
    </div>
  );
} 