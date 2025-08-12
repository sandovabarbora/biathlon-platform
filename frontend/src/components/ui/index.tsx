// frontend/src/components/ui/index.tsx
import { ReactNode, ButtonHTMLAttributes, HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'
import { Loader2, AlertCircle, CheckCircle, XCircle, Info } from 'lucide-react'

// ============= BUTTON COMPONENT =============
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  icon?: ReactNode
}

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  className,
  disabled,
  ...props
}: ButtonProps) => {
  const baseStyles = 'inline-flex items-center justify-center font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'

  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-purple-600 text-white hover:bg-purple-700 focus:ring-purple-500',
    outline: 'border-2 border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-sm rounded-md',
    md: 'px-4 py-2 text-base rounded-lg',
    lg: 'px-6 py-3 text-lg rounded-lg',
  }

  return (
    <button
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      ) : icon ? (
        <span className="mr-2">{icon}</span>
      ) : null}
      {children}
    </button>
  )
}

// ============= CARD COMPONENT =============
interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'bordered' | 'elevated'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export const Card = ({
  children,
  variant = 'default',
  padding = 'md',
  className,
  ...props
}: CardProps) => {
  const variants = {
    default: 'bg-white',
    bordered: 'bg-white border border-gray-200',
    elevated: 'bg-white shadow-lg',
  }

  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }

  return (
    <div
      className={cn(
        'rounded-xl transition-all duration-200',
        variants[variant],
        paddings[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

// ============= BADGE COMPONENT =============
interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
  size?: 'sm' | 'md'
}

export const Badge = ({
  children,
  variant = 'default',
  size = 'md',
  className,
  ...props
}: BadgeProps) => {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </span>
  )
}

// ============= STAT CARD COMPONENT =============
interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: ReactNode
  trend?: {
    value: number
    label: string
  }
  variant?: 'default' | 'primary' | 'success' | 'warning'
}

export const StatCard = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  variant = 'default'
}: StatCardProps) => {
  const variantStyles = {
    default: 'bg-white',
    primary: 'bg-gradient-to-br from-blue-500 to-blue-600 text-white',
    success: 'bg-gradient-to-br from-green-500 to-green-600 text-white',
    warning: 'bg-gradient-to-br from-yellow-500 to-yellow-600 text-white',
  }

  const isColored = variant !== 'default'

  return (
    <Card
      className={cn(
        'relative overflow-hidden',
        variantStyles[variant],
        isColored ? 'border-0' : ''
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className={cn(
            "text-sm font-medium",
            isColored ? 'text-white/90' : 'text-gray-600'
          )}>
            {title}
          </p>
          <p className={cn(
            "text-3xl font-bold mt-2",
            isColored ? 'text-white' : 'text-gray-900'
          )}>
            {value}
          </p>
          {subtitle && (
            <p className={cn(
              "text-sm mt-1",
              isColored ? 'text-white/80' : 'text-gray-500'
            )}>
              {subtitle}
            </p>
          )}
          {trend && (
            <div className="flex items-center mt-2">
              <span className={cn(
                "text-sm font-medium",
                trend.value > 0 ? 'text-green-600' : 'text-red-600',
                isColored && 'text-white'
              )}>
                {trend.value > 0 ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className={cn(
                "text-sm ml-2",
                isColored ? 'text-white/80' : 'text-gray-500'
              )}>
                {trend.label}
              </span>
            </div>
          )}
        </div>
        {icon && (
          <div className={cn(
            "p-3 rounded-lg",
            isColored ? 'bg-white/20' : 'bg-gray-100'
          )}>
            {icon}
          </div>
        )}
      </div>
    </Card>
  )
}

// ============= ALERT COMPONENT =============
interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'error'
  title?: string
  dismissible?: boolean
  onDismiss?: () => void
}

export const Alert = ({
  children,
  variant = 'info',
  title,
  dismissible = false,
  onDismiss,
  className,
  ...props
}: AlertProps) => {
  const icons = {
    info: <Info className="w-5 h-5" />,
    success: <CheckCircle className="w-5 h-5" />,
    warning: <AlertCircle className="w-5 h-5" />,
    error: <XCircle className="w-5 h-5" />,
  }

  const styles = {
    info: 'bg-blue-50 text-blue-800 border-blue-200',
    success: 'bg-green-50 text-green-800 border-green-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    error: 'bg-red-50 text-red-800 border-red-200',
  }

  return (
    <div
      className={cn(
        'rounded-lg border p-4 flex',
        styles[variant],
        className
      )}
      {...props}
    >
      <div className="flex-shrink-0">{icons[variant]}</div>
      <div className="ml-3 flex-1">
        {title && <h3 className="text-sm font-semibold mb-1">{title}</h3>}
        <div className="text-sm">{children}</div>
      </div>
      {dismissible && (
        <button
          onClick={onDismiss}
          className="ml-3 inline-flex rounded-md p-1.5 hover:bg-black/5 transition-colors"
        >
          <XCircle className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}

// ============= LOADING SPINNER =============
interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export const Spinner = ({ size = 'md', className }: SpinnerProps) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  }

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <Loader2 className={cn(sizes[size], 'animate-spin text-blue-600')} />
    </div>
  )
}

// ============= SKELETON LOADER =============
interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
}

export const Skeleton = ({
  variant = 'text',
  width,
  height,
  className,
  ...props
}: SkeletonProps) => {
  const variants = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  }

  return (
    <div
      className={cn(
        'animate-pulse bg-gray-200',
        variants[variant],
        className
      )}
      style={{
        width: width || (variant === 'circular' ? '40px' : '100%'),
        height: height || (variant === 'circular' ? '40px' : variant === 'text' ? '16px' : '60px'),
      }}
      {...props}
    />
  )
}

// ============= TABS COMPONENT =============
interface TabsProps {
  tabs: Array<{
    id: string
    label: string
    icon?: ReactNode
    badge?: string | number
  }>
  activeTab: string
  onChange: (tabId: string) => void
  className?: string
}

export const Tabs = ({ tabs, activeTab, onChange, className }: TabsProps) => {
  return (
    <div className={cn('border-b border-gray-200', className)}>
      <nav className="-mb-px flex space-x-8">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={cn(
              'group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            )}
          >
            {tab.icon && <span className="mr-2">{tab.icon}</span>}
            {tab.label}
            {tab.badge && (
              <Badge
                size="sm"
                variant={activeTab === tab.id ? 'info' : 'default'}
                className="ml-2"
              >
                {tab.badge}
              </Badge>
            )}
          </button>
        ))}
      </nav>
    </div>
  )
}

// ============= EMPTY STATE =============
interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
}

export const EmptyState = ({ icon, title, description, action }: EmptyStateProps) => {
  return (
    <div className="text-center py-12">
      {icon && (
        <div className="mx-auto w-12 h-12 text-gray-400 mb-4">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      {description && (
        <p className="text-sm text-gray-500 mb-4 max-w-sm mx-auto">
          {description}
        </p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  )
}