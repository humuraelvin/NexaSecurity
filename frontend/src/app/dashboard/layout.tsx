"use client";
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
  Scan,
  BotIcon,
  PanelLeft,
  PanelRight,
} from "lucide-react";
import { useAuthContext } from "@/providers/AuthProvider";
import Image from "next/image";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [expanded, setExpanded] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useAuthContext();

  // Load state from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem("sidebarExpanded");
    if (savedState !== null) {
      setExpanded(JSON.parse(savedState));
    }
  }, []);

  // Save state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("sidebarExpanded", JSON.stringify(expanded));
  }, [expanded]);

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
      name: "AI Agent",
      href: "/dashboard/agent",
      icon: <BotIcon className="h-5 w-5" />,
    },
    {
      name: "Settings",
      href: "/dashboard/settings",
      icon: <Settings className="h-5 w-5" />,
    },
  ];

  // Helper function to handle navigation
  const handleNavigation = (href: string) => {
    router.push(href);
  };

  // Check if a link is active
  const isLinkActive = (href: string) => {
    if (href === "/dashboard") {
      return pathname === href;
    }
    return pathname?.startsWith(href);
  };

  const toggleSidebar = () => {
    setExpanded((prev) => !prev);
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-b from-gray-950 to-gray-900 text-white">
      {/* Sidebar */}
      <div
        className={`sticky top-0 h-screen bg-gray-900/90 backdrop-blur-sm border-r border-gray-800 
          transition-all duration-300 ease-in-out z-30
          ${expanded ? "w-64" : "w-20"}`}
      >
        <div className="flex flex-col h-full">
          <div
            className={`flex items-center h-16 border-b border-gray-800 ${
              expanded ? "justify-between px-4" : "justify-center"
            }`}
          >
            <Link href="/" className="flex items-center">
              <Image
                src="/logo.png"
                width={64}
                height={64}
                alt="NexaSec Logo"
                className={`${expanded ? "h-16" : "h-10 w-10"}`}
              />
            </Link>

            {expanded ? (
              <button
                onClick={toggleSidebar}
                className="text-gray-400 hover:text-white"
              >
                <PanelLeft className="h-5 w-5" />
              </button>
            ) : null}
          </div>

          <nav
            className={`flex-1 py-6 space-y-1 overflow-y-auto ${
              expanded ? "px-4" : "px-2"
            }`}
          >
            {navItems.map((item) => (
              <button
                key={item.name}
                onClick={() => handleNavigation(item.href)}
                className={`flex items-center w-full rounded-md transition-colors ${
                  expanded ? "px-4 py-3 text-left" : "p-3 justify-center"
                } ${
                  isLinkActive(item.href)
                    ? "bg-cyan-900/30 text-cyan-400 border-l-4 border-cyan-400"
                    : "text-gray-400 hover:bg-gray-800/60 hover:text-white"
                }`}
                title={!expanded ? item.name : undefined}
              >
                {item.icon}
                {expanded && <span className="ml-3">{item.name}</span>}
              </button>
            ))}
          </nav>

          <div
            className={`p-4 border-t border-gray-800 ${
              !expanded && "flex justify-center"
            }`}
          >
            {!expanded && (
              <button
                onClick={toggleSidebar}
                className="text-gray-400 hover:text-white p-2"
              >
                <PanelRight className="h-5 w-5" />
              </button>
            )}

            {expanded && (
              <button
                onClick={logout}
                className="flex items-center w-full px-4 py-3 text-gray-400 rounded-md hover:bg-gray-800/60 hover:text-white transition-colors"
              >
                <LogOut className="h-5 w-5 text-cyan-400" />
                <span className="ml-3">Logout</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Mobile toggle button (only visible on small screens) */}
      <div className="fixed bottom-4 right-4 z-40 md:hidden">
        <button
          onClick={toggleSidebar}
          className="p-3 rounded-full bg-gray-800/80 text-gray-400 hover:text-white focus:outline-none shadow-lg"
        >
          {expanded ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-x-hidden">{children}</main>
      </div>
    </div>
  );
}
