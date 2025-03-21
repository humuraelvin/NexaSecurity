import { motion } from "framer-motion";
import { MessageCircleIcon } from "lucide-react";

export const Overview = () => {
  return (
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.5 }}
    >
      <div className="rounded-xl p-6 flex flex-col gap-8 leading-relaxed text-center max-w-xl">
        <p className="flex flex-row justify-center gap-4 items-center">
          <MessageCircleIcon size={32} />
        </p>
        <p className="text-2xl font-semibold">Nexa AI</p>
        <p className="text-base text-gray-300">
          Your comprehensive security Assistant. Learn, Monitor, analyze, and
          protect your digital assets with advanced threat detection and
          real-time response capabilities.
        </p>
      </div>
    </motion.div>
  );
};
