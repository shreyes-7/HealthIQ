import { Outlet, useLocation, Link } from 'react-router-dom'
import AppSidebar from '@/components/AppSidebar'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
  BreadcrumbLink,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import { Home, Sparkles } from 'lucide-react'

const PAGE_TITLES = [
  { match: (path) => path === '/app', title: 'Executive Dashboard' },
  { match: (path) => path.startsWith('/app/predict'), title: 'Patient Triage Prediction' },
  { match: (path) => path.startsWith('/app/explainability'), title: 'SHAP Explainability Studio' },
  { match: (path) => path.startsWith('/app/history'), title: 'Prediction History Archive' },
  { match: (path) => path.startsWith('/app/about'), title: 'About & Model Architecture' },
]

function usePageTitle() {
  const { pathname } = useLocation()
  return PAGE_TITLES.find((entry) => entry.match(pathname))?.title ?? 'HealthIQ'
}

export default function AppLayout() {
  const pageTitle = usePageTitle()

  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="min-w-0 bg-background text-foreground">
        <header className="sticky top-0 z-30 flex h-14 shrink-0 items-center justify-between gap-2 border-b bg-background/95 backdrop-blur-md px-4 transition-all">
          <div className="flex items-center gap-2">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden sm:inline-flex">
                  <BreadcrumbLink asChild>
                    <Link to="/" className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors">
                      <Home className="size-3.5" />
                      <span>Home</span>
                    </Link>
                  </BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden sm:inline-flex" />
                <BreadcrumbItem>
                  <BreadcrumbPage className="font-semibold tracking-tight text-foreground">{pageTitle}</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>

          <div className="flex items-center gap-2">
            <Button asChild variant="outline" size="sm" className="hidden sm:flex gap-1.5 text-xs font-medium h-8">
              <Link to="/app/predict">
                <Sparkles className="size-3.5 text-primary" />
                <span>New Prediction</span>
              </Link>
            </Button>
          </div>
        </header>

        <div className="min-w-0 flex-1 space-y-6 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
