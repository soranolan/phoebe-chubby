# 鳴潮：小團快跑 模擬分析器 (Phoebe Chubby Simulator)

這是一個簡單的小團快跑模擬賽分析器。

## 核心規則說明

### 1. 堆疊與帶動位移 (Stacking & Towing)
*   **後到者居上**：多個團子移動到同一格時，後到的團子會疊在原有堆疊的上方。
*   **底層帶動**：當位於堆疊下方的團子移動時，會帶著其上方所有的團子一起移動。若上方的團子自己移動，則不會影響下方的團子。
*   **起跑線公平性**：所有團子從 **1 號位** 出發。在第一回合從起點移動時，團子之間互不帶動（並排起跑）。

### 2. 行動順序 (Action Order)
*   **每輪隨機**：每一回合開始前，系統會隨機打亂所有角色的發車順序，這決定了誰會先發車、誰會被誰載走。

### 3. 地圖機關 (Map Effects)
賽道總長 32 格，特定位置設有機關：
*   **前進裝置 (3, 11, 16, 23)**：物理強制推向 32 方向 1 格。
*   **倒退陷阱 (10, 28)**：物理強制推向 1 方向 1 格。
*   **空間裂隙 (6, 20)**：隨機重組該格的堆疊順序。

## 執行方式

詳細轉播（單場）：
```bash
python3 -m src.phoebe_chubby.main
```

數據分析（批次）：
```bash
python3 -m src.phoebe_chubby.analysis 1000000
```

## 如何執行

### 單場模擬
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 -m phoebe_chubby.main
```

### 批量分析
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 -m phoebe_chubby.analysis 10000
```
