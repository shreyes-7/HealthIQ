import { Outlet, useLocation } from 'react-router-dom'
import AppSidebar from '@/components/AppSidebar'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'

const PAGE_TITLES = [
  { match: (path) => path === '/app', title: 'Dashboard' },
  { match: (path) => path.startsWith('/app/predict'), title: 'Patient Prediction' },
  { match: (path) => path.startsWith('/app/explainability'), title: 'Model Explainability' },
  { match: (path) => path.startsWith('/app/history'), title: 'Prediction History' },
  { match: (path) => path.startsWith('/app/about'), title: 'About' },
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
      <SidebarInset className="min-w-0">
        <header className="flex h-14 shrink-0 items-center gap-2 border-b bg-background px-4">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbPage className="font-medium text-foreground">{pageTitle}</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        {/* SidebarInset already renders the <main> landmark -- this is a plain
            content wrapper, not a second <main>, to keep the page to exactly
            one <main> landmark for assistive tech. */}
        <div className="min-w-0 flex-1 space-y-6 p-6">
          <Outlet />
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
