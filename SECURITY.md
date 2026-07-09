# Security Policy

HarnessLab is an educational project. It demonstrates secure-harness patterns for long-horizon multi-agent systems without live secrets, cloud credentials, paid model APIs, or production data.

Please do not file public issues containing real credentials, private customer data, or exploit details against a live third-party system. If a vulnerability is found in the HarnessLab teaching code, open a private report through GitHub security advisories when available, or contact the maintainers directly.

The project intentionally includes simulated unsafe paths so students can observe how the harness blocks, escalates, quarantines, or rolls back risky behavior. A failing unsafe path inside a lab scenario is not automatically a vulnerability; it may be the intended teaching case. A security issue is a bug that allows the lab framework, CLI, package, or documented workflow to leak secrets, execute untrusted code unexpectedly, bypass the stated control contract, or mislead students about a security property.

