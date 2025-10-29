import React from 'react';
import { Card, CardContent } from '../ui/card';
import { cn } from '../../lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const StatCard = ({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  trendValue,
  description,
  color = 'indigo',
  onClick 
}) => {
  const colorClasses = {
    indigo: {
      bg: 'bg-indigo-50',
      text: 'text-indigo-600',
      gradient: 'from-indigo-600 to-blue-500'
    },
    green: {
      bg: 'bg-green-50',
      text: 'text-green-600',
      gradient: 'from-green-600 to-emerald-500'
    },
    orange: {
      bg: 'bg-orange-50',
      text: 'text-orange-600',
      gradient: 'from-orange-600 to-amber-500'
    },
    red: {
      bg: 'bg-red-50',
      text: 'text-red-600',
      gradient: 'from-red-600 to-rose-500'
    },
    purple: {
      bg: 'bg-purple-50',
      text: 'text-purple-600',
      gradient: 'from-purple-600 to-violet-500'
    },
    blue: {
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      gradient: 'from-blue-600 to-cyan-500'
    }
  };

  const colors = colorClasses[color] || colorClasses.indigo;

  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend === 'up') return <TrendingUp className="w-4 h-4" />;
    if (trend === 'down') return <TrendingDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-600';
    if (trend === 'down') return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <Card 
      className={cn(
        'hover:shadow-lg transition-all duration-300 border-0 shadow-sm',
        onClick && 'cursor-pointer hover:scale-105'
      )}
      onClick={onClick}
    >
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
            <h3 className="text-3xl font-bold text-gray-900 mb-2">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </h3>
            
            {/* Trend or Description */}
            {(trend || description) && (
              <div className="flex items-center gap-2 text-sm">
                {trend && (
                  <span className={cn('flex items-center gap-1 font-medium', getTrendColor())}>
                    {getTrendIcon()}
                    {trendValue && <span>{trendValue}</span>}
                  </span>
                )}
                {description && (
                  <span className="text-gray-500">{description}</span>
                )}
              </div>
            )}
          </div>

          {/* Icon */}
          {Icon && (
            <div className={cn('p-3 rounded-xl', colors.bg)}>
              <Icon className={cn('w-6 h-6', colors.text)} />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default StatCard;
