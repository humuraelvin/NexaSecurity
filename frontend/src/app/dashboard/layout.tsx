"use client"
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { 
  LayoutDashboard, 
  Network, 
  ShieldAlert, 
  FileBarChart, 
  Settings, 
  LogOut,
  Menu,
  X,
  Terminal,
  Scan
} from "lucide-react";
import { useAuthContext } from "@/providers/AuthProvider";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user } = useAuthContext();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useAuthContext();

  const navItems = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: <LayoutDashboard className="h-5 w-5" />,
    },
    {
      name: "Network",
      href: "/dashboard/network",
      icon: <Network className="h-5 w-5" />,
    },
    {
      name: "Network Scan",
      href: "/dashboard/network-scan",
      icon: <Scan className="h-5 w-5" />,
    },
    {
      name: "Vulnerabilities",
      href: "/dashboard/vulnerabilities",
      icon: <ShieldAlert className="h-5 w-5" />,
    },
    {
      name: "Penetration Testing",
      href: "/dashboard/pentest",
      icon: <Terminal className="h-5 w-5" />,
    },
    {
      name: "Reports",
      href: "/dashboard/reports",
      icon: <FileBarChart className="h-5 w-5" />,
    },
    {
      name: "Settings",
      href: "/dashboard/settings",
      icon: <Settings className="h-5 w-5" />,
    },
  ];

  // Helper function to handle navigation
  const handleNavigation = (href: string) => {
    setSidebarOpen(false); // Close sidebar on mobile
    router.push(href);
  };

  // Check if a link is active
  const isLinkActive = (href: string) => {
    if (href === "/dashboard") {
      return pathname === href;
    }
    return pathname?.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 to-gray-900 text-white flex">
      {/* Mobile sidebar toggle */}
      <div className="fixed top-4 left-4 z-40 md:hidden">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-md bg-gray-800/80 text-gray-400 hover:text-white focus:outline-none"
        >
          {sidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-gray-900/90 backdrop-blur-sm border-r border-gray-800 transform transition-transform duration-300 ease-in-out ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } md:translate-x-0 md:static md:h-screen`}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-center h-16 border-b border-gray-800">
            <Link href="/" className="flex items-center">
              <img src="/logo.png" alt="NexaSec Logo" className="h-16" />
            </Link>
          </div>

          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            {navItems.map((item) => (
              <button
                key={item.name}
                onClick={() => handleNavigation(item.href)}
                className={`flex items-center w-full px-4 py-3 rounded-md transition-colors text-left ${
                  isLinkActive(item.href)
                    ? "bg-cyan-900/30 text-cyan-400 border-l-4 border-cyan-400"
                    : "text-gray-400 hover:bg-gray-800/60 hover:text-white"
                }`}
              >
                {item.icon}
                <span className="ml-3">{item.name}</span>
              </button>
            ))}
          </nav>

          <div className="p-4 border-t border-gray-800">
            <button
              onClick={logout}
              className="flex items-center w-full px-4 py-3 text-gray-400 rounded-md hover:bg-gray-800/60 hover:text-white transition-colors"
            >
              <LogOut className="h-5 w-5 text-cyan-400" />
              <span className="ml-3">Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 md:p-6">
          {/* Use key to force remount when path changes */}
          <div key={pathname}>
            {children}
          </div>
        </main>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 md:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
} 