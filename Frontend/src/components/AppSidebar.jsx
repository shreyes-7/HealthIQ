import { Activity, ClipboardPlus, Info, LayoutDashboard, Sparkles } from 'lucide-react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'

const PRIMARY_NAV_ITEMS = [
  { to: '/app', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/app/predict', label: 'Prediction', icon: ClipboardPlus },
  { to: '/app/explainability', label: 'Explainability', icon: Sparkles },
  { to: '/app/history', label: 'Prediction History', icon: Activity },
]

const SECONDARY_NAV_ITEMS = [{ to: '/app/about', label: 'About', icon: Info }]

function isRouteActive(pathname, to, end) {
  if (end) return pathname === to
  return pathname === to || pathname.startsWith(`${to}/`)
}

function NavMenu({ items, pathname }) {
  return (
    <SidebarMenu>
      {items.map((item) => {
        const active = isRouteActive(pathname, item.to, item.end)
        return (
          <SidebarMenuItem key={item.to}>
            <SidebarMenuButton asChild isActive={active} tooltip={item.label}>
              <NavLink to={item.to} end={item.end}>
                <item.icon />
                <span>{item.label}</span>
              </NavLink>
            </SidebarMenuButton>
          </SidebarMenuItem>
        )
      })}
    </SidebarMenu>
  )
}

export default function AppSidebar() {
  const { pathname } = useLocation()

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <Link to="/" className="flex items-center gap-2 rounded-md px-2 py-1.5 outline-none focus-visible:ring-3 focus-visible:ring-ring/50">
          <div className="flex size-7 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <Activity className="size-4" />
          </div>
          <span className="text-base font-semibold tracking-tight group-data-[collapsible=icon]:hidden">
            HealthIQ
          </span>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Platform</SidebarGroupLabel>
          <SidebarGroupContent>
            <NavMenu items={PRIMARY_NAV_ITEMS} pathname={pathname} />
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup className="mt-auto">
          <SidebarGroupContent>
            <NavMenu items={SECONDARY_NAV_ITEMS} pathname={pathname} />
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
