"""MCP sunucusu: motoru çağıran ince adaptör. Hesap mantığı burada YOKTUR; powerlab.cli.compute çağrılır."""
from mcp.server.fastmcp import FastMCP
from powerlab.cli import compute

mcp = FastMCP("powerlab")


@mcp.tool()
def power_analysis_t_paired(mode: str, tails: int, dz: float, alpha: float,
                            power: float | None = None, n: int | None = None) -> dict:
    """Eşleştirilmiş (bağımlı) iki ortalama için t testi güç analizi.
    mode="a-priori": power verilir, gerekli çift sayısı N hesaplanır.
    mode="post-hoc": n (çift sayısı) verilir, güç hesaplanır.
    dz: etki büyüklüğü (fark ortalaması / fark standart sapması), tails: 1 ya da 2.
    Dönüş: n_total, n1, n2, actual_power, power, critical, df, ncp ya da {"error": ...}."""
    return compute(mode=mode, tails=tails, dz=dz, alpha=alpha, power=power, n=n)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
